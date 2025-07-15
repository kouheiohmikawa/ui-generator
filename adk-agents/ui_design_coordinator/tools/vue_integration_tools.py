import os
import json
import re
from typing import Dict, List, Any
from pathlib import Path

def generate_vue_component(component_name: str, template: str, script: str, style: str) -> Dict[str, Any]:
    """新しいVue.jsコンポーネントを生成"""
    try:
        component_content = f"""<template>
{template}
</template>

<script setup>
{script}
</script>

<style scoped>
{style}
</style>
"""
        
        # src/components/に保存
        file_path = f"../src/components/{component_name}.vue"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(component_content)
        
        return {
            "status": "success",
            "file_path": file_path,
            "component_name": component_name,
            "message": f"{component_name}.vue を生成しました"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def modify_existing_component(file_path: str, modifications: Dict[str, str]) -> Dict[str, Any]:
    """既存のVue.jsコンポーネントを修正"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # バックアップ作成
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 修正を適用
        modified_content = apply_modifications(content, modifications)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return {
            "status": "success",
            "file_path": file_path,
            "backup_path": backup_path,
            "modifications_applied": list(modifications.keys()),
            "message": "コンポーネントを修正しました"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def apply_modifications(content: str, modifications: Dict[str, str]) -> str:
    """修正を適用"""
    modified_content = content
    
    for section, new_content in modifications.items():
        if section == "template":
            # テンプレートセクションを置換
            modified_content = re.sub(
                r'<template[^>]*>(.*?)</template>',
                f'<template>\n{new_content}\n</template>',
                modified_content,
                flags=re.DOTALL
            )
        elif section == "script":
            # スクリプトセクションを置換
            modified_content = re.sub(
                r'<script[^>]*>(.*?)</script>',
                f'<script setup>\n{new_content}\n</script>',
                modified_content,
                flags=re.DOTALL
            )
        elif section == "style":
            # スタイルセクションを置換
            modified_content = re.sub(
                r'<style[^>]*>(.*?)</style>',
                f'<style scoped>\n{new_content}\n</style>',
                modified_content,
                flags=re.DOTALL
            )
    
    return modified_content

def integrate_vuetify_component(base_template: str, vuetify_components: List[str]) -> str:
    """Vuetifyコンポーネントをテンプレートに統合"""
    enhanced_template = base_template
    
    # Vuetifyコンポーネントのマッピング
    vuetify_mapping = {
        "button": {"from": r'<button([^>]*)>', "to": r'<v-btn\1>'},
        "input": {"from": r'<input([^>]*)>', "to": r'<v-text-field\1>'},
        "card": {"from": r'<div class="card"([^>]*)>', "to": r'<v-card\1>'},
        "form": {"from": r'<form([^>]*)>', "to": r'<v-form\1>'}
    }
    
    for component in vuetify_components:
        if component in vuetify_mapping:
            mapping = vuetify_mapping[component]
            enhanced_template = re.sub(
                mapping["from"],
                mapping["to"],
                enhanced_template
            )
    
    return enhanced_template

def analyze_project_structure() -> Dict[str, Any]:
    """プロジェクト構造を分析"""
    try:
        structure = {
            "vue_components": [],
            "package_json": None,
            "vite_config": None,
            "dependencies": []
        }
        
        # src/components/のVueファイルを取得
        components_dir = Path("../src/components")
        if components_dir.exists():
            structure["vue_components"] = [
                f.name for f in components_dir.glob("*.vue")
            ]
        
        # package.jsonを分析
        package_json_path = Path("../package.json")
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                structure["package_json"] = package_data
                structure["dependencies"] = list(package_data.get("dependencies", {}).keys())
        
        return {
            "status": "success",
            "structure": structure,
            "vuetify_installed": "vuetify" in structure["dependencies"],
            "project_type": "Vue 3 + Vite"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def generate_improved_signup_component(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """SignUpコンポーネントの改善版を生成"""
    
    # 分析結果に基づいて改善されたテンプレートを生成
    improved_template = """  <v-container class="signup-container">
    <v-row justify="center">
      <v-col cols="12" md="6" lg="4">
        <v-card class="signup-card" elevation="8">
          <v-card-title class="signup-title">
            <h2>アカウント作成</h2>
          </v-card-title>
          
          <v-card-text>
            <v-form ref="signupForm" v-model="isFormValid">
              <v-text-field
                v-model="email"
                label="メールアドレス"
                type="email"
                :rules="emailRules"
                variant="outlined"
                prepend-inner-icon="mdi-email"
                required
              />
              
              <v-text-field
                v-model="password"
                label="パスワード"
                :type="showPassword ? 'text' : 'password'"
                :rules="passwordRules"
                variant="outlined"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                required
              />
              
              <v-text-field
                v-model="confirmPassword"
                label="パスワード確認"
                :type="showConfirmPassword ? 'text' : 'password'"
                :rules="confirmPasswordRules"
                variant="outlined"
                prepend-inner-icon="mdi-lock-check"
                :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
                required
              />
              
              <v-btn
                :disabled="!isFormValid || isLoading"
                :loading="isLoading"
                color="success"
                size="large"
                variant="elevated"
                block
                @click="handleSignup"
                class="signup-button"
              >
                アカウント作成
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>"""
    
    improved_script = """import { ref, computed } from 'vue'

const isFormValid = ref(false)
const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const emailRules = [
  v => !!v || 'メールアドレスは必須です',
  v => /.+@.+\..+/.test(v) || 'メールアドレスの形式が正しくありません'
]

const passwordRules = [
  v => !!v || 'パスワードは必須です',
  v => v.length >= 8 || 'パスワードは8文字以上で入力してください',
  v => /[A-Z]/.test(v) || 'パスワードには大文字を含めてください',
  v => /[0-9]/.test(v) || 'パスワードには数字を含めてください'
]

const confirmPasswordRules = [
  v => !!v || 'パスワード確認は必須です',
  v => v === password.value || 'パスワードが一致しません'
]

const handleSignup = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  
  try {
    // サインアップ処理をここに実装
    console.log('サインアップ処理', {
      email: email.value,
      password: password.value
    })
    
    // 成功時の処理
    alert('アカウントが正常に作成されました')
    
  } catch (error) {
    console.error('サインアップエラー:', error)
    alert('エラーが発生しました。再度お試しください。')
  } finally {
    isLoading.value = false
  }
}"""
    
    improved_style = """.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
}

.signup-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(46, 125, 50, 0.1);
  transition: all 0.3s ease;
}

.signup-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(46, 125, 50, 0.15);
}

.signup-title {
  text-align: center;
  padding: 24px 24px 16px;
  background: linear-gradient(45deg, #2e7d32, #388e3c);
  color: white;
  border-radius: 16px 16px 0 0;
}

.signup-title h2 {
  margin: 0;
  font-weight: 300;
  font-size: 1.5rem;
}

.signup-button {
  margin-top: 16px;
  height: 48px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.5px;
}

.v-text-field {
  margin-bottom: 8px;
}

.v-card-text {
  padding: 24px;
}"""
    
    return {
        "status": "success",
        "improved_component": {
            "template": improved_template,
            "script": improved_script,
            "style": improved_style,
            "filename": "ImprovedSignUp.vue"
        },
        "improvements": [
            "パスワード強度のバリデーション追加",
            "視覚的なフィードバック改善",
            "アクセシビリティの向上",
            "レスポンシブデザインの最適化",
            "エラーハンドリングの実装",
            "ローディング状態の表示"
        ]
    }

def update_app_vue_imports(new_components: List[str]) -> Dict[str, Any]:
    """App.vueのimport文を更新"""
    try:
        app_vue_path = "../src/App.vue"
        
        if not os.path.exists(app_vue_path):
            return {"status": "error", "message": "App.vueファイルが見つかりません"}
        
        with open(app_vue_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 新しいimport文を追加
        for component in new_components:
            import_line = f"import {component} from './components/{component}.vue'"
            if import_line not in content:
                # script setup セクションに追加
                script_match = re.search(r'(<script setup>)(.*?)(</script>)', content, re.DOTALL)
                if script_match:
                    before = script_match.group(1)
                    current_content = script_match.group(2)
                    after = script_match.group(3)
                    
                    new_content = f"{before}\n{import_line}{current_content}{after}"
                    content = content.replace(script_match.group(0), new_content)
        
        # ファイルを更新
        with open(app_vue_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": "App.vueを更新しました",
            "components_added": new_components
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_component_from_template(template_name: str, customizations: Dict[str, Any]) -> Dict[str, Any]:
    """テンプレートからコンポーネントを作成"""
    
    templates = {
        "form": {
            "template": "<v-form><v-text-field label='入力してください' /></v-form>",
            "script": "import { ref } from 'vue'\nconst formData = ref('')",
            "style": ".v-form { padding: 16px; }"
        },
        "card": {
            "template": "<v-card><v-card-title>タイトル</v-card-title></v-card>",
            "script": "// カード用のスクリプト",
            "style": ".v-card { margin: 16px; }"
        }
    }
    
    if template_name not in templates:
        return {"status": "error", "message": f"テンプレート '{template_name}' が見つかりません"}
    
    base_template = templates[template_name]
    
    # カスタマイゼーションを適用
    customized_template = base_template.copy()
    for key, value in customizations.items():
        if key in customized_template:
            customized_template[key] = value
    
    return {
        "status": "success",
        "component": customized_template,
        "message": f"テンプレート '{template_name}' からコンポーネントを作成しました"
    } 