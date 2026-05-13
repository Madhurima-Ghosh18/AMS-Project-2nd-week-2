import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index    from "./pages/Index";
import Tickets  from "./pages/Tickets";
import Runbooks from "./pages/Runbooks";
import LogsPage from "./pages/LogsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"          element={<Index />}    />
        <Route path="/tickets"   element={<Tickets />}  />
        <Route path="/runbooks"  element={<Runbooks />} />
        <Route path="/logs"      element={<LogsPage/>} />
      </Routes>
    </BrowserRouter>
  );
}