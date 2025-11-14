import { Outlet } from "react-router-dom"; 
import Header from "../components/layout/Header";

function MainLayout() {
    return (
        <div className="body-div">
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