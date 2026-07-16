import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Sidebar from './components/Sidebar'
import Toast from './components/Toast'
import { ToastProvider } from './components/Toast'

import TemplatePage from './pages/TemplatePage'
import CandidatePage from './pages/CandidatePage'
import GeneratorPage from './pages/GeneratorPage'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <div
          className="flex h-screen overflow-hidden"
          style={{ background: 'var(--bg-base)' }}
        >
          <Sidebar />

          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/templates" element={<TemplatePage />} />
              <Route path="/candidates" element={<CandidatePage />} />
              <Route path="/generator" element={<GeneratorPage />} />
              <Route path="/" element={<Navigate to="/templates" replace />} />
            </Routes>
          </main>
        </div>
        <Toast />
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
