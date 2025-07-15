<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="10" class="signup-card">
          <v-card-title class="text-center pa-6">
            <v-icon size="48" color="primary" class="mb-4">mdi-account-plus</v-icon>
            <h2 class="text-h4 font-weight-bold primary--text">サインアップ</h2>
          </v-card-title>
          
          <v-card-text class="pa-6">
            <v-form @submit.prevent="handleSubmit" ref="form">
              <v-text-field
                v-model="email"
                label="メールアドレス"
                prepend-inner-icon="mdi-email"
                type="email"
                variant="outlined"
                color="primary"
                :rules="emailRules"
                required
                class="mb-4"
              />
              
              <v-text-field
                v-model="password"
                label="パスワード"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                color="primary"
                :rules="passwordRules"
                required
                class="mb-4"
              />
              
              <v-text-field
                v-model="confirmPassword"
                label="パスワード確認"
                prepend-inner-icon="mdi-lock-check"
                :type="showConfirmPassword ? 'text' : 'password'"
                :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
                variant="outlined"
                color="primary"
                :rules="confirmPasswordRules"
                required
                class="mb-4"
              />
              
              <v-alert
                v-if="errorMessage"
                type="error"
                class="mb-4"
                dismissible
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
              
              <v-alert
                v-if="successMessage"
                type="success"
                class="mb-4"
                dismissible
                @click:close="successMessage = ''"
              >
                {{ successMessage }}
              </v-alert>
              
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                class="mb-4"
              >
                <v-icon left>mdi-account-plus</v-icon>
                サインアップ
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-card-actions class="pa-6 pt-0">
            <v-spacer />
            <div class="text-center">
              <span class="text-body-2">すでにアカウントをお持ちですか？</span>
              <v-btn
                variant="text"
                color="primary"
                @click="$emit('switch-to-login')"
              >
                ログイン
              </v-btn>
            </div>
            <v-spacer />
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['switch-to-login'])

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const form = ref(null)

// バリデーションルール
const emailRules = [
  v => !!v || 'メールアドレスは必須です',
  v => /.+@.+\..+/.test(v) || '有効なメールアドレスを入力してください'
]

const passwordRules = [
  v => !!v || 'パスワードは必須です',
  v => v.length >= 6 || 'パスワードは6文字以上で入力してください'
]

const confirmPasswordRules = [
  v => !!v || 'パスワード確認は必須です',
  v => v === password.value || 'パスワードが一致しません'
]

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // フォームバリデーション
  const { valid } = await form.value.validate()
  
  if (!valid) {
    errorMessage.value = 'すべての項目を正しく入力してください'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'パスワードが一致しません'
    return
  }
  
  loading.value = true
  
  try {
    // サインアップ処理のシミュレーション
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('サインアップ:', {
      email: email.value,
      password: password.value
    })
    
    successMessage.value = 'サインアップが完了しました！'
    
    // フォームリセット
    setTimeout(() => {
      form.value.reset()
      email.value = ''
      password.value = ''
      confirmPassword.value = ''
    }, 2000)
    
  } catch (error) {
    errorMessage.value = 'サインアップに失敗しました。再度お試しください。'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signup-card {
  background: linear-gradient(135deg, #f0f9f0 0%, #d4e6d4 100%);
  border-radius: 20px !important;
}

.fill-height {
  min-height: 100vh;
}

.v-card-title {
  background: linear-gradient(135deg, #2ed573 0%, #1e7e34 100%);
  color: white !important;
  border-radius: 20px 20px 0 0 !important;
}

.v-card-title .v-icon {
  color: white !important;
}

.v-card-title h2 {
  color: white !important;
}

.v-btn {
  border-radius: 25px !important;
  text-transform: none !important;
  font-weight: 500 !important;
}

.v-text-field {
  border-radius: 15px !important;
}

/* カスタムグラデーション背景 */
.v-container {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}
</style>