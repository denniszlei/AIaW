import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'

const isAuthenticated = ref(false)
const isDialogVisible = ref(false)

export function useAccessCode() {
  async function checkAuthStatus() {
    try {
      const response = await api.get('/api/auth/status')
      isAuthenticated.value = response.data.authenticated
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
      const response = await api.post('/api/auth/verify', { code })
      if (response.data.status === 'success') {
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
