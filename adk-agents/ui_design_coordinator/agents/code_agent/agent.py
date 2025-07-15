from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import FunctionTool
from .prompt import CODE_AGENT_INSTRUCTION

# 環境変数を読み込み
load_dotenv()

def generate_vue_component_code(component_spec: dict) -> dict:
    """コンポーネント仕様からVue.jsコードを生成する"""
    
    # 仮の実装 - 後で詳細を追加
    template = """<template>
  <v-card class="signup-card" elevation="4">
    <v-card-title class="text-h5">
      {{ title }}
    </v-card-title>
    <v-card-text>
      <v-form v-model="isFormValid">
        <v-text-field
          v-model="email"
          label="メールアドレス"
          type="email"
          :rules="emailRules"
          required
        />
        <v-text-field
          v-model="password"
          label="パスワード"
          type="password"
          :rules="passwordRules"
          required
        />
        <v-btn
          :disabled="!isFormValid"
          color="success"
          @click="handleSubmit"
          block
        >
          登録
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>"""
    
    script = r"""<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'アカウント作成'
  }
})

const emit = defineEmits(['submit'])

const isFormValid = ref(false)
const email = ref('')
const password = ref('')

const emailRules = [
  v => !!v || 'メールアドレスは必須です',
  v => /.+@.+\..+/.test(v) || 'メールアドレスの形式が正しくありません'
]

const passwordRules = [
  v => !!v || 'パスワードは必須です',
  v => v.length >= 8 || 'パスワードは8文字以上で入力してください'
]

const handleSubmit = () => {
  if (isFormValid.value) {
    emit('submit', {
      email: email.value,
      password: password.value
    })
  }
}
</script>"""
    
    style = """<style scoped>
.signup-card {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.v-card-title {
  text-align: center;
  color: #2E7D32;
}
</style>"""
    
    return {
        "status": "success",
        "vue_code": {
            "template": template,
            "script": script,
            "style": style,
            "filename": "ImprovedSignUp.vue"
        }
    }

def modify_existing_vue_file(file_path: str, modifications: dict) -> dict:
    """既存のVue.jsファイルを修正する"""
    
    # 仮の実装 - 後で詳細を追加
    return {
        "status": "success",
        "modifications": {
            "file_path": file_path,
            "changes_made": ["色彩の調整", "バリデーションの追加", "アクセシビリティの改善"],
            "backup_created": f"{file_path}.backup"
        }
    }

def create_code_agent():
    """開発補助エージェントを作成"""
    
    # ツールを作成
    generate_tool = FunctionTool(func=generate_vue_component_code)
    modify_tool = FunctionTool(func=modify_existing_vue_file)
    
    # エージェントを作成
    agent = Agent(
        name="code_agent",
        model="gemini-1.5-flash-8b",
        description="Vue.jsコードの実装と修正を行う専門エージェント",
        instruction=CODE_AGENT_INSTRUCTION,
        tools=[generate_tool, modify_tool]
    )
    
    return agent 