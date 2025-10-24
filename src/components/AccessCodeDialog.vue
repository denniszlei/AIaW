<template>
  <q-dialog v-model="isDialogVisible" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Access Code Required</div>
      </q-card-section>

      <q-card-section>
        <q-input
          v-model="accessCode"
          label="Access Code"
          @keyup.enter="verify"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Submit" color="primary" @click="verify" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAccessCode } from '../composables/access-code'

const { isDialogVisible, verifyAccessCode } = useAccessCode()

const accessCode = ref('')

async function verify() {
  await verifyAccessCode(accessCode.value)
}
</script>
