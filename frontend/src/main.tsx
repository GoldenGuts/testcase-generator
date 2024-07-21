import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./approute";
import "./index.css";
import { Navbar, Nav, OverlayTrigger, Tooltip } from "react-bootstrap";
import Cookies from "js-cookie";
// import * as dotenv from 'dotenv';

// dotenv.config(); // Load environment variables
const getTooltipMessage = () => {
  const xrayExists = Cookies.get("xray");
  const jiraExists = Cookies.get("jira");

  if (xrayExists && jiraExists) {
    return "All Authenticated";
  } else if (xrayExists) {
    return "Jira unauthorized";
  } else if (jiraExists) {
    return "XRay unauthorized";
  } else {
    return "No authentication yet";
  }
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <div className="navbar">
      <img src="/new-logo.png" alt="Logo for Litera" className="navbar-logo" />
      <div className="navbar-icon">
        <Nav.Link href="/">
          <i className="fa-solid fa-house"></i>
        </Nav.Link>
        <OverlayTrigger
          placement="bottom"
          overlay={
            <Tooltip id="tooltip-settings">{getTooltipMessage()}</Tooltip>
          }
        >
          <Nav.Link href="/settings">
            <i
              className={`fas fa-cog ${
                Cookies.get("xray") && Cookies.get("jira") ? "green-icon" : ""
              }`}
            ></i>
          </Nav.Link>
        </OverlayTrigger>
      </div>
    </div>
    {process.env.REACT_APP_ENABLE_VECTOR_API === 'true' && !Cookies.get("vectorization_api_key") && (
      <div style={{ color: "red", textAlign: "center", marginTop: "20px" }}>
        Warning: Vectorization API key is not present.
      </div>
    )}
    <AppRouter></AppRouter>
  </React.StrictMode>
);
