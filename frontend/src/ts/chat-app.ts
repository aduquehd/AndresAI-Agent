// @ts-ignore - External ES module
import { marked } from "https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js";

// Declare Notyf as global (loaded via script tag)
declare const Notyf: any;

// Configure marked to open links in new tabs
const renderer = new marked.Renderer();
const originalLinkRenderer = renderer.link.bind(renderer);
renderer.link = (href: string, title: string | null, text: string) => {
  const html = originalLinkRenderer(href, title, text);
  return html.replace("<a ", '<a target="_blank" rel="noopener noreferrer" ');
};
marked.setOptions({ renderer });

// DOM Elements with proper typing
const convElement = document.getElementById("conversation") as HTMLDivElement | null;
const promptInput = document.getElementById("prompt-input") as HTMLInputElement | null;
const spinner = document.getElementById("spinner") as HTMLDivElement | null;
const newChatBtn = document.getElementById("new-chat-btn") as HTMLButtonElement | null;
const formElement = document.querySelector("form") as HTMLFormElement | null;
const themeToggle = document.getElementById("theme-toggle") as HTMLButtonElement | null;

// Initialize Notyf with default styles
const notyf = new Notyf({
  duration: 6000,
  position: {
    x: 'right',
    y: 'top',
  },
  dismissible: true,
  ripple: true,
});

// Constants
const STORAGE_KEY = "chat_user_id";
const BROWSER_ID_KEY = "chat_browser_id";
const API_ENDPOINTS = {
  sendMessage: "/api/chats/send",
  chatHistory: "/api/chats/history",
} as const;

// Types
interface Message {
  role: "user" | "assistant" | "model";
  content: string;
  timestamp: string;
}

interface ChatState {
  userId: string;
  browserId: string;
  isLoading: boolean;
  hasMessages: boolean;
}

interface RateLimitError {
  error: string;
  message: string;
  retry_after: number;
}

// State management
const state: ChatState = {
  userId: "",
  browserId: "",
  isLoading: false,
  hasMessages: false,
};

// Utility functions
function generateUUID(): string {
  // Use crypto API if available for better randomness
  if (crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback to manual generation
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getUserId(): string {
  let userId = localStorage.getItem(STORAGE_KEY);

  if (!userId) {
    userId = generateUUID();
    localStorage.setItem(STORAGE_KEY, userId);
  }

  return userId;
}

function getBrowserId(): string {
  let browserId = localStorage.getItem(BROWSER_ID_KEY);

  if (!browserId) {
    browserId = generateUUID();
    localStorage.setItem(BROWSER_ID_KEY, browserId);
  }

  return browserId;
}

function createAuthHeaders(): HeadersInit {
  return {
    Authorization: `User-Id ${state.userId}`,
    "X-Browser-Id": state.browserId,
  };
}

// UI State Management
function setLoadingState(loading: boolean): void {
  state.isLoading = loading;

  if (spinner) {
    spinner.classList.toggle("active", loading);
  }

  if (promptInput) {
    promptInput.disabled = loading;

    // Also update the wrapper styling
    const inputWrapper = promptInput.closest(".input-wrapper");
    if (inputWrapper) {
      inputWrapper.classList.toggle("disabled", loading);
    }
  }

  // Disable/enable the new chat button
  if (newChatBtn) {
    newChatBtn.disabled = loading;
  }
}

function showError(error: Error | string, customMessage?: string, suppressConsole = false): void {
  // Only log to console if not suppressed (e.g., for rate limiting)
  if (!suppressConsole) {
    console.error("Chat error:", error);
  }

  let message: string;
  
  if (customMessage) {
    message = customMessage;
  } else if (typeof error === "string") {
    message = error;
  } else {
    message = error.message || "An error occurred. Please try again.";
  }

  // Show error notification using Notyf
  notyf.error(message);

  setLoadingState(false);
}

function showSuccess(message: string): void {
  notyf.success(message);
}

// Chat UI Functions
function clearConversation(): void {
  if (convElement) {
    convElement.innerHTML = "";
  }
  state.hasMessages = false;
}

function toggleNewChatButton(show: boolean): void {
  const newChatContainer = document.querySelector(".new-chat-container");
  if (newChatContainer) {
    newChatContainer.classList.toggle("show", show);
  }
}

function startNewChat(): void {
  const newUserId = generateUUID();
  localStorage.setItem(STORAGE_KEY, newUserId);
  state.userId = newUserId;

  clearConversation();
  toggleNewChatButton(false);

  if (promptInput) {
    promptInput.focus();
  }
}

// Message Rendering
function createMessageElement(message: Message): HTMLDivElement {
  const msgDiv = document.createElement("div");
  msgDiv.id = `msg-${message.timestamp}`;
  msgDiv.className = `message ${message.role === "user" ? "user" : "model"}`;
  msgDiv.innerHTML = marked.parse(message.content);
  return msgDiv;
}

function renderMessage(message: Message): void {
  if (!convElement) return;

  const existingMsg = document.getElementById(`msg-${message.timestamp}`);

  if (!existingMsg) {
    const msgElement = createMessageElement(message);
    convElement.appendChild(msgElement);
    state.hasMessages = true;
  } else {
    // Update existing message content
    existingMsg.innerHTML = marked.parse(message.content);
  }
}

function scrollToBottom(): void {
  if (convElement) {
    convElement.scrollTop = convElement.scrollHeight;
  }
}

// API Communication
function parseMessages(responseText: string): Message[] {
  return responseText
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => {
      try {
        return JSON.parse(line) as Message;
      } catch (e) {
        console.warn("Failed to parse message:", line, e);
        return null;
      }
    })
    .filter((msg): msg is Message => msg !== null);
}

async function handleApiError(response: Response): Promise<never> {
  const errorText = await response.text();
  
  // Handle rate limiting specifically
  if (response.status === 429) {
    try {
      const rateLimitError: RateLimitError = JSON.parse(errorText);
      const retryAfter = rateLimitError.retry_after || 60;
      const minutes = Math.ceil(retryAfter / 60);
      const errorMessage = `Rate limit exceeded. Please wait ${minutes} minute${minutes > 1 ? 's' : ''} before sending another message.`;
      throw new Error(errorMessage);
    } catch (parseError) {
      throw new Error("Too many requests. Please wait a moment and try again.");
    }
  }
  
  // Handle other HTTP errors
  if (response.status === 500) {
    throw new Error("Server error. Please try again later.");
  } else if (response.status === 503) {
    throw new Error("Service temporarily unavailable. Please try again later.");
  } else if (response.status >= 400 && response.status < 500) {
    throw new Error(`Request failed: ${errorText || response.statusText}`);
  } else {
    throw new Error(`Server error (${response.status}): ${errorText || response.statusText}`);
  }
}

async function streamResponse(response: Response): Promise<void> {
  if (!response.ok) {
    await handleApiError(response);
  }

  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete messages from buffer
      const messages = parseMessages(buffer);
      messages.forEach(renderMessage);

      // Only show new chat button after first user message
      if (state.hasMessages) {
        toggleNewChatButton(true);
      }

      scrollToBottom();
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      const messages = parseMessages(buffer);
      messages.forEach(renderMessage);
      scrollToBottom();
    }
  } finally {
    reader.releaseLock();
    setLoadingState(false);

    // Ensure input is re-enabled and focused
    if (promptInput) {
      promptInput.disabled = false;
      promptInput.focus();

      // Ensure wrapper styling is updated
      const inputWrapper = promptInput.closest(".input-wrapper");
      if (inputWrapper) {
        inputWrapper.classList.remove("disabled");
      }
    }

    // Ensure new chat button is re-enabled
    if (newChatBtn) {
      newChatBtn.disabled = false;
    }
  }
}

async function sendMessage(content: string): Promise<void> {
  setLoadingState(true);

  const formData = new FormData();
  formData.append("prompt", content);

  try {
    const response = await fetch(API_ENDPOINTS.sendMessage, {
      method: "POST",
      body: formData,
      headers: createAuthHeaders(),
    });

    await streamResponse(response);

    if (promptInput) {
      promptInput.value = "";
    }
  } catch (error) {
    if (error instanceof Error) {
      // Check if it's a rate limit error based on the message
      const isRateLimitError = error.message.includes("Rate limit") || error.message.includes("Too many requests");
      showError(error, error.message, isRateLimitError);
    } else {
      showError(new Error("Failed to send message"));
    }
    // Don't throw to prevent console errors - error is already shown to user
  } finally {
    setLoadingState(false);
  }
}

async function loadChatHistory(): Promise<void> {
  try {
    setLoadingState(true);

    const response = await fetch(API_ENDPOINTS.chatHistory, {
      headers: createAuthHeaders(),
    });

    if (!response.ok) {
      // Always handle API errors, including rate limiting
      await handleApiError(response);
    }

    const responseText = await response.text();

    // Check if there are existing messages
    if (responseText.trim()) {
      const messages = parseMessages(responseText);
      messages.forEach(renderMessage);

      if (messages.length > 0) {
        toggleNewChatButton(true);
        scrollToBottom();
      }
    }

    setLoadingState(false);
  } catch (error) {
    // Show all errors to the user
    if (error instanceof Error) {
      // Check if it's a rate limit error based on the message
      const isRateLimitError = error.message.includes("Rate limit") || error.message.includes("Too many requests");
      showError(error, error.message, isRateLimitError);
    } else {
      showError(new Error("Failed to load chat history"));
    }
  }
}

// Event Handlers
async function handleSubmit(e: SubmitEvent): Promise<void> {
  e.preventDefault();

  const formData = new FormData(e.target as HTMLFormElement);
  const prompt = formData.get("prompt") as string;

  if (!prompt?.trim()) return;

  await sendMessage(prompt);
}

// Theme Management
const THEME_KEY = "chat_theme";

function getStoredTheme(): string {
  return localStorage.getItem(THEME_KEY) || "dark";
}

function setTheme(theme: string): void {
  const root = document.documentElement;
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');

  if (theme === "light") {
    root.setAttribute("data-theme", "light");
    if (metaThemeColor) {
      metaThemeColor.setAttribute("content", "#ffffff");
    }
  } else {
    root.removeAttribute("data-theme");
    if (metaThemeColor) {
      metaThemeColor.setAttribute("content", "#0a0a0f");
    }
  }

  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme(): void {
  const currentTheme = getStoredTheme();
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  setTheme(newTheme);
}

// Initialize
function initialize(): void {
  // Initialize theme
  const storedTheme = getStoredTheme();
  setTheme(storedTheme);

  // Initialize state
  state.userId = getUserId();
  state.browserId = getBrowserId();

  // Attach event listeners
  if (formElement) {
    formElement.addEventListener("submit", (e) => {
      handleSubmit(e).catch((error) => {
        // Error is already handled in sendMessage
        // Don't log rate limit errors to console
        const isRateLimitError = error?.message?.includes("Rate limit") || error?.message?.includes("Too many requests");
        if (!isRateLimitError) {
          console.error("Submit error:", error);
        }
      });
    });
  }

  if (newChatBtn) {
    newChatBtn.addEventListener("click", startNewChat);
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }

  // Load chat history
  loadChatHistory().catch((error) => {
    // Don't log rate limit errors to console
    const isRateLimitError = error?.message?.includes("Rate limit") || error?.message?.includes("Too many requests");
    if (!isRateLimitError) {
      console.error("Failed to load chat history:", error);
    }
  });
}

// Start the application
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialize);
} else {
  initialize();
}
