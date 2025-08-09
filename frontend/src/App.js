import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import EmalfDraw from "./components/EmalfDraw";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<EmalfDraw />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;