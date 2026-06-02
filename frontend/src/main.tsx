import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { App } from "./App";
import { AppQueryClientProvider } from "./context/query-client";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppQueryClientProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AppQueryClientProvider>
  </React.StrictMode>
);
