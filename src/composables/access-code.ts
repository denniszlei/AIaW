import { ref, onMounted } from 'vue'

const isAuthenticated = ref(false)
const isDialogVisible = ref(false)

export function useAccessCode() {
  async function checkAuthStatus() {
    try {
      const response = await fetch('/api/auth/status')
      const data = await response.json()
      isAuthenticated.value = data.authenticated
      if (!isAuthenticated.value) {
        isDialogVisible.value = true
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      isDialogVisible.value = true
    }
  }

  async function verifyAccessCode(code: string) {
    try {
      const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code })
      })
      const data = await response.json()
      if (data.status === 'success') {
        isAuthenticated.value = true
        isDialogVisible.value = false
      } else {
        // Handle error
      }
    } catch (error) {
      console.error('Error verifying access code:', error)
    }
  }

  onMounted(checkAuthStatus)

  return {
    isAuthenticated,
    isDialogVisible,
    verifyAccessCode,
    checkAuthStatus
  }
}
