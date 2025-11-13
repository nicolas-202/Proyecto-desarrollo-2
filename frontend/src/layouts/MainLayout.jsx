import { Outlet } from "react-router-dom"; 
import Header from "../components/layout/Header";

function MainLayout() {
    return (
        <div style={{
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            background: "linear-gradient(135deg, #F4A261 0%, #FF6B35 100%)",
            minHeight: "100vh",
            color: "#2C3E50",
            width: "100%",
            margin: 0,
            padding: 0
        }}>
            <Header />
            
            {/* Panel de notificaciones (como en tu prototipo) */}
            <div className="notifications-panel" id="notifications-panel"></div>
            
            {/* Área principal de contenido */}
            <main className="main-content">
                <Outlet /> {/* Renderiza la página actual */}
            </main>
        </div>
    )
}
export default MainLayout;