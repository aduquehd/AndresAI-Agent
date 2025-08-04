// Copy email function
export function copyEmail(): void {
  const email = "aduquehd@gmail.com";
  navigator.clipboard
    .writeText(email)
    .then(() => {
      // Create and show feedback
      const feedback = document.createElement("div");
      feedback.className = "copy-feedback";
      feedback.textContent = "Email Copied!";
      document.body.appendChild(feedback);

      // Remove feedback after animation
      setTimeout(() => {
        document.body.removeChild(feedback);
      }, 2000);
    })
    .catch((err: Error) => {
      console.error("Failed to copy email: ", err);
    });
}

// Focus input when page loads
function focusInput(): void {
  const input = document.getElementById("prompt-input") as HTMLInputElement | null;
  if (input) {
    // Use setTimeout to ensure DOM is fully loaded
    setTimeout(() => {
      input.focus();
    }, 100);
  }
}

// Focus on page load and when returning from background
document.addEventListener("DOMContentLoaded", focusInput);
window.addEventListener("load", focusInput);
window.addEventListener("pageshow", focusInput);

// Make function globally available for onclick attribute
declare global {
  interface Window {
    copyEmail: typeof copyEmail;
  }
}
window.copyEmail = copyEmail;
