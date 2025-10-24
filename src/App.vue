<template>
  <router-view />
  <AccessCodeDialog />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useFirstVisit } from './composables/first-visit'
import { useLoginDialogs } from './composables/login-dialogs'
import { useSetTheme } from './composables/set-theme'
import { useSubscriptionNotify } from './composables/subscription-notify'
import { onMounted } from 'vue'
import { checkUpdate, ready } from './utils/update'
import AccessCodeDialog from './components/AccessCodeDialog.vue'
import { useAccessCode } from './composables/access-code'

defineOptions({
  name: 'App'
})

useSetTheme()
useLoginDialogs()
useFirstVisit()
useSubscriptionNotify()
useAccessCode()

const router = useRouter()
router.afterEach(to => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI as Workspace`
  }
})

onMounted(() => {
  ready()
  checkUpdate()
})

</script>
