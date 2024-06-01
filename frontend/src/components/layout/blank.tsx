import React from "react";
import { Navbar, Nav, OverlayTrigger, Tooltip } from "react-bootstrap";
import Cookies from "js-cookie";
import "./blank.css";

interface BlankLayoutProps {
  children: React.ReactNode;
}
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

const BlankLayout: React.FC<BlankLayoutProps> = ({ children }) => {

  return (
    <div className="blank-layout">

      {/* Main content area */}
      <div className="main-content">{children}</div>
    </div>
  );
};

export default BlankLayout;
