# deploy_frontend.py
import os
from pathlib import Path

def deploy_frontend():
    print("🚀 DEPLOYING FRONTEND CONFIGURATION (Svelte 5 + Tauri v2)...")
    
    ROOT = Path.cwd()
    TAURI_DIR = ROOT / "src-tauri"
    FRONTEND_SRC = TAURI_DIR / "src"
    
    # 1. Package.json với dependencies chính xác
    package_json = '''{
  "name": "convert-vault",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.1.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.1.0",
    "vite": "^5.0.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "svelte": "^5.0.0",
    "typescript": "^5.0.0",
    "@tsconfig/svelte": "^5.0.0"
  }
}'''
    
    # 2. Vite config đơn giản
    vite_config = '''import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 1420,
    strictPort: true,
  },
  clearScreen: false,
});'''
    
    # 3. Tauri config
    tauri_conf = '''{
  "$schema": "../node_modules/@tauri-apps/cli/config.schema.json",
  "app": {
    "withGlobalTauri": false,
    "windows": [
      {
        "title": "Convert Vault",
        "width": 800,
        "height": 600
      }
    ]
  },
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:1420",
    "frontendDist": "../dist"
  }
}'''
    
    # 4. TypeScript config
    tsconfig = '''{
  "extends": "@tsconfig/svelte/tsconfig.json",
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "resolveJsonModule": true,
    "allowJs": true,
    "checkJs": true,
    "isolatedModules": true
  },
  "include": ["src/**/*.ts", "src/**/*.js", "src/**/*.svelte"]
}'''
    
    # 5. Svelte component đơn giản
    app_svelte = '''<script>
  import { onMount } from 'svelte';
  
  let status = 'Loading...';
  
  onMount(async () => {
    try {
      if (window.__TAURI__) {
        const { invoke } = await import('@tauri-apps/api/core');
        // Note: We are calling 'export_recovery_qr' which is the command we registered in lib.rs
        // But for initial test, let's just show connection status.
        // If we want to test the command, we need to pass arguments.
        status = '✅ Frontend Ready (Svelte 5 + Tauri v2)';
      } else {
        status = '⚠️ Running in browser mode';
      }
    } catch (error) {
      status = '❌ Error: ' + error;
    }
  });
</script>

<div style="padding: 20px; font-family: sans-serif;">
  <h1>🛡️ Convert Vault</h1>
  <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <p>{status}</p>
  </div>
  <p>Frontend is running with Svelte 5 + Tauri v2</p>
</div>'''
    
    # 6. Main TypeScript file
    main_ts = '''import { mount } from 'svelte';
import App from './App.svelte';

const app = mount(App, {
  target: document.getElementById('app')!,
});

export default app;'''
    
    # 7. HTML entry point
    index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Convert Vault</title>
    <style>
      body { margin: 0; padding: 0; font-family: system-ui, sans-serif; }
      #app { min-height: 100vh; }
    </style>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>'''
    
    # Tạo thư mục và file
    try:
        FRONTEND_SRC.mkdir(parents=True, exist_ok=True)
        
        # Write configuration files
        (TAURI_DIR / "package.json").write_text(package_json, encoding='utf-8')
        print("✅ Created package.json")
        
        (TAURI_DIR / "vite.config.js").write_text(vite_config, encoding='utf-8')
        print("✅ Created vite.config.js")
        
        (TAURI_DIR / "tauri.conf.json").write_text(tauri_conf, encoding='utf-8')
        print("✅ Created tauri.conf.json")
        
        (TAURI_DIR / "tsconfig.json").write_text(tsconfig, encoding='utf-8')
        print("✅ Created tsconfig.json")
        
        # Write source files
        (TAURI_DIR / "index.html").write_text(index_html, encoding='utf-8')
        print("✅ Created index.html")
        
        (FRONTEND_SRC / "main.ts").write_text(main_ts, encoding='utf-8')
        print("✅ Created main.ts")
        
        (FRONTEND_SRC / "App.svelte").write_text(app_svelte, encoding='utf-8')
        print("✅ Created App.svelte")
        
        print("\n🎉 FRONTEND CONFIGURATION COMPLETED!")
        print("👉 Next steps:")
        print("   cd src-tauri")
        print("   npm install")
        print("   npm run tauri dev")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying frontend: {e}")
        return False

if __name__ == "__main__":
    success = deploy_frontend()
    if not success:
        print("\n💥 Frontend deployment failed. Please check errors above.")
