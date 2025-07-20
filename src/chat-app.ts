// @ts-ignore - External ES module
import { marked } from 'https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js'

// DOM Elements with proper typing
const convElement = document.getElementById('conversation') as HTMLDivElement | null
const promptInput = document.getElementById('prompt-input') as HTMLInputElement | null
const spinner = document.getElementById('spinner') as HTMLDivElement | null
const errorElement = document.getElementById('error') as HTMLDivElement | null
const newChatBtn = document.getElementById('new-chat-btn') as HTMLButtonElement | null
const formElement = document.querySelector('form') as HTMLFormElement | null

// Constants
const STORAGE_KEY = 'chat_user_id'
const API_ENDPOINTS = {
  sendMessage: '/api/chats/send',
  chatHistory: '/api/chats/history'
} as const

// Types
interface Message {
  role: 'user' | 'assistant' | 'model'
  content: string
  timestamp: string
}

interface ChatState {
  userId: string
  isLoading: boolean
  hasMessages: boolean
}

// State management
const state: ChatState = {
  userId: '',
  isLoading: false,
  hasMessages: false
}

// Utility functions
function generateUUID(): string {
  // Use crypto API if available for better randomness
  if (crypto.randomUUID) {
    return crypto.randomUUID()
  }
  
  // Fallback to manual generation
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function getUserId(): string {
  let userId = localStorage.getItem(STORAGE_KEY)
  
  if (!userId) {
    userId = generateUUID()
    localStorage.setItem(STORAGE_KEY, userId)
  }
  
  return userId
}

function createAuthHeaders(): HeadersInit {
  return {
    'Authorization': `User-Id ${state.userId}`
  }
}

// UI State Management
function setLoadingState(loading: boolean): void {
  state.isLoading = loading
  
  if (spinner) {
    spinner.classList.toggle('active', loading)
  }
  
  if (promptInput) {
    promptInput.disabled = loading
    
    // Also update the wrapper styling
    const inputWrapper = promptInput.closest('.input-wrapper')
    if (inputWrapper) {
      inputWrapper.classList.toggle('disabled', loading)
    }
  }
  
  // Disable/enable the new chat button
  if (newChatBtn) {
    newChatBtn.disabled = loading
  }
}

function showError(error: Error): void {
  console.error('Chat error:', error)
  
  if (errorElement) {
    errorElement.classList.remove('d-none')
  }
  
  setLoadingState(false)
}

function clearError(): void {
  if (errorElement) {
    errorElement.classList.add('d-none')
  }
}

// Chat UI Functions
function clearConversation(): void {
  if (convElement) {
    convElement.innerHTML = ''
  }
  state.hasMessages = false
}

function toggleNewChatButton(show: boolean): void {
  const newChatContainer = document.querySelector('.new-chat-container')
  if (newChatContainer) {
    newChatContainer.classList.toggle('show', show)
  }
}

function startNewChat(): void {
  const newUserId = generateUUID()
  localStorage.setItem(STORAGE_KEY, newUserId)
  state.userId = newUserId
  
  clearConversation()
  toggleNewChatButton(false)
  
  if (promptInput) {
    promptInput.focus()
  }
}

// Message Rendering
function createMessageElement(message: Message): HTMLDivElement {
  const msgDiv = document.createElement('div')
  msgDiv.id = `msg-${message.timestamp}`
  msgDiv.className = `message ${message.role === 'user' ? 'user' : 'model'}`
  msgDiv.innerHTML = marked.parse(message.content)
  return msgDiv
}

function renderMessage(message: Message): void {
  if (!convElement) return
  
  const existingMsg = document.getElementById(`msg-${message.timestamp}`)
  
  if (!existingMsg) {
    const msgElement = createMessageElement(message)
    convElement.appendChild(msgElement)
    state.hasMessages = true
  } else {
    // Update existing message content
    existingMsg.innerHTML = marked.parse(message.content)
  }
}

function scrollToBottom(): void {
  if (convElement) {
    convElement.scrollTop = convElement.scrollHeight
  }
}

// API Communication
function parseMessages(responseText: string): Message[] {
  return responseText
    .split('\n')
    .filter(line => line.trim())
    .map(line => {
      try {
        return JSON.parse(line) as Message
      } catch (e) {
        console.warn('Failed to parse message:', line, e)
        return null
      }
    })
    .filter((msg): msg is Message => msg !== null)
}

async function streamResponse(response: Response): Promise<void> {
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Server error: ${response.status} - ${errorText}`)
  }
  
  if (!response.body) {
    throw new Error('No response body')
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      
      // Process complete messages from buffer
      const messages = parseMessages(buffer)
      messages.forEach(renderMessage)
      
      // Only show new chat button after first user message
      if (state.hasMessages) {
        toggleNewChatButton(true)
      }
      
      scrollToBottom()
    }
    
    // Process any remaining buffer
    if (buffer.trim()) {
      const messages = parseMessages(buffer)
      messages.forEach(renderMessage)
      scrollToBottom()
    }
  } finally {
    reader.releaseLock()
    setLoadingState(false)
    
    // Ensure input is re-enabled and focused
    if (promptInput) {
      promptInput.disabled = false
      promptInput.focus()
      
      // Ensure wrapper styling is updated
      const inputWrapper = promptInput.closest('.input-wrapper')
      if (inputWrapper) {
        inputWrapper.classList.remove('disabled')
      }
    }
    
    // Ensure new chat button is re-enabled
    if (newChatBtn) {
      newChatBtn.disabled = false
    }
  }
}

async function sendMessage(content: string): Promise<void> {
  clearError()
  setLoadingState(true)
  
  const formData = new FormData()
  formData.append('prompt', content)
  
  try {
    const response = await fetch(API_ENDPOINTS.sendMessage, {
      method: 'POST',
      body: formData,
      headers: createAuthHeaders()
    })
    
    await streamResponse(response)
    
    if (promptInput) {
      promptInput.value = ''
    }
  } catch (error) {
    showError(error instanceof Error ? error : new Error('Unknown error'))
    throw error
  } finally {
    setLoadingState(false)
  }
}

async function loadChatHistory(): Promise<void> {
  try {
    setLoadingState(true)
    
    const response = await fetch(API_ENDPOINTS.chatHistory, {
      headers: createAuthHeaders()
    })
    
    const responseText = await response.text()
    
    // Check if there are existing messages
    if (responseText.trim()) {
      const messages = parseMessages(responseText)
      messages.forEach(renderMessage)
      
      if (messages.length > 0) {
        toggleNewChatButton(true)
        scrollToBottom()
      }
    }
    
    setLoadingState(false)
  } catch (error) {
    showError(error instanceof Error ? error : new Error('Failed to load chat history'))
  }
}

// Event Handlers
async function handleSubmit(e: SubmitEvent): Promise<void> {
  e.preventDefault()
  
  const formData = new FormData(e.target as HTMLFormElement)
  const prompt = formData.get('prompt') as string
  
  if (!prompt?.trim()) return
  
  await sendMessage(prompt)
}

// Initialize
function initialize(): void {
  // Initialize state
  state.userId = getUserId()
  
  // Attach event listeners
  if (formElement) {
    formElement.addEventListener('submit', (e) => {
      handleSubmit(e).catch(error => {
        showError(error instanceof Error ? error : new Error('Failed to send message'))
      })
    })
  }
  
  if (newChatBtn) {
    newChatBtn.addEventListener('click', startNewChat)
  }
  
  // Load chat history
  loadChatHistory().catch(error => {
    console.error('Failed to load chat history:', error)
  })
}

// Start the application
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize)
} else {
  initialize()
}