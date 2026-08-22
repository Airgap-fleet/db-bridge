// src/App.tsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardMCPClient } from './mcp-client';
import { FleetOverview } from './components/FleetOverview';
import { AgentDetail } from './components/AgentDetail';
import { DeploymentPanel } from './components/DeploymentPanel';
import { DeploymentProgress } from './components/DeploymentProgress';
import { MetricsCharts } from './components/MetricsCharts';
import { AlertBanner } from './components/AlertBanner';
import { Sidebar } from './components/Sidebar';
import './index.css';

const queryClient = new QueryClient();
const client = new DashboardMCPClient('http://localhost:8001/mcp');

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <AlertBanner />
          
          {/* Mobile sidebar overlay */}
          {isSidebarOpen && (
            <div 
              className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
              onClick={() => setIsSidebarOpen(false)}
            />
          )}
          
          {/* Sidebar */}
          <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
          
          {/* Main content */}
          <div className="lg:ml-64 min-h-screen">
            <header className="bg-card border-b px-4 py-4 lg:px-8">
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md hover:bg-muted"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-2xl font-bold mt-2">AFaaS Fleet Dashboard</h1>
            </header>
            
            <main className="p-4 lg:p-8">
              <Routes>
                <Route path="/" element={<FleetOverview />} />
                <Route path="/agents/:agentId" element={<AgentDetail />} />
                <Route path="/deployments" element={<DeploymentPanel />} />
                <Route path="/deployments/:deploymentId" element={<DeploymentProgress />} />
                <Route path="/metrics" element={<MetricsCharts />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}