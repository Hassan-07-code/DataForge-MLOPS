import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import "./Layout.css";

function MainLayout() {

    return (

        <div className="layout">

            <Sidebar />

            <div className="content">

                <Navbar />

                <main className="page-content">

                    <Outlet />

                </main>

            </div>

        </div>

    );

}

export default MainLayout;