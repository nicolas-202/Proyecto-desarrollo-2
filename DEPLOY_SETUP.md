# Deploy Hooks Configurados

## Backend
- Deploy Hook: Configurado en GitHub Secrets
- URL: https://rifasplus-backend.onrender.com (actualizar con tu URL real)

## Frontend  
- Deploy Hook: Configurado en GitHub Secrets
- URL: https://rifasplus-frontend.onrender.com (actualizar con tu URL real)

## GitHub Secrets
- RENDER_BACKEND_DEPLOY_HOOK ✅
- RENDER_FRONTEND_DEPLOY_HOOK ✅
- SECRET_KEY ✅

## Flujo Automático
1. git push origin main
2. GitHub Actions ejecuta tests
3. Construye imágenes Docker
4. Despliega automáticamente a Render
5. Backend y Frontend actualizados en ~5 minutos

## Monitorear Deploys
- GitHub: https://github.com/nicolas-202/Proyecto-desarrollo-2/actions
- Render: https://dashboard.render.com
