import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Search,
  Target,
  Terminal,
  Send,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Cpu,
  Mail,
  ChevronRight,
  Loader2,
  Copy,
  Zap,
  Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [domain, setDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [trace, setTrace] = useState([]);
  const traceEndRef = useRef(null);

  const scrollToBottom = () => {
    traceEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [trace]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!domain) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setTrace(["Initializing autonomous intelligence engine..."]);

    try {
      // Mocking trace for visual feedback while waiting for API
      // Since our API currently returns all at once, we'll simulate the "journey"
      const res = await axios.post(`${API_BASE_URL}/analyze`, { domain });

      // Simulate steps for better UX
      for (const step of res.data.agent_trace) {
        setTrace(prev => [...prev, step]);
        await new Promise(r => setTimeout(r, 800));
      }

      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to analyze domain. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="min-h-screen w-full px-4 py-8 lg:px-12">
      {/* Header */}
      <header className="max-w-7xl mx-auto flex flex-col items-center mb-12">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 mb-4"
        >
          <div className="p-2 bg-brand-500 rounded-xl shadow-lg shadow-brand-500/20">
            <Zap className="text-white w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Vexstorm <span className="text-brand-400">Intelligence</span>
          </h1>
        </motion.div>
        <p className="text-gray-400 text-center max-w-xl">
          Beyond the search bar. Our autonomous agents research pivots, tech debt, and fiscal pressures to find your next enterprise partner.
        </p>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Input & Trace */}
        <div className="lg:col-span-5 space-y-6">
          <section className="glass rounded-3xl p-8 glow-card">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
              <Globe className="w-6 h-6 text-brand-400" />
              Analyze Company
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="relative group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-brand-400 w-5 h-5 transition-colors" />
                <input
                  type="text"
                  placeholder="e.g. acme-robotics.com"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 transition-all placeholder:text-gray-600"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading || !domain}
                className="w-full bg-brand-600 hover:bg-brand-500 active:scale-[0.98] disabled:opacity-50 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 transition-all shadow-xl shadow-brand-600/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Autonomous Search Active...
                  </>
                ) : (
                  <>
                    <Target className="w-5 h-5" />
                    Engage Strategic SDR
                  </>
                )}
              </button>
            </form>
            {error && (
              <p className="text-red-400 mt-4 text-sm bg-red-400/10 p-3 rounded-xl border border-red-400/20">
                {error}
              </p>
            )}
          </section>

          {/* Agent Journey Trace */}
          <section className="glass rounded-3xl p-6 h-[400px] flex flex-col">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Terminal className="w-5 h-5 text-green-400" />
              Research Journey
            </h2>
            <div className="flex-1 overflow-y-auto font-mono text-sm space-y-2 pr-2 custom-scrollbar">
              <AnimatePresence initial={false}>
                {trace.map((step, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-gray-300 border-l-2 border-brand-500/30 pl-3 py-1"
                  >
                    <span className="text-brand-500 mr-2">›</span>
                    {step}
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={traceEndRef} />
            </div>
          </section>
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-7 space-y-6">
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full min-h-[400px] glass rounded-3xl border-dashed border-white/10 flex flex-col items-center justify-center text-gray-500"
              >
                <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                  <Cpu className="w-8 h-8 opacity-20" />
                </div>
                <p>Awaiting Autonomous Analysis</p>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-6"
              >
                {/* Dossier Card */}
                <div className="glass rounded-3xl p-8 glow-card">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-1 truncate">
                        {result.company_dossier.title || domain}
                      </h3>
                      <p className="text-brand-400 font-medium">{result.company_dossier.industry}</p>
                    </div>
                    <div className={`px-4 py-2 rounded-full font-bold flex items-center gap-2 ${result.verdict.recommendation === 'YES'
                      ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                      : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                      {result.verdict.recommendation === 'YES' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                      {result.verdict.recommendation}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Analysis Signals</h4>
                      <p className="text-gray-300 bg-white/5 p-4 rounded-2xl italic leading-relaxed">
                        "{result.company_dossier.summary}"
                      </p>
                    </div>
                    <div className="space-y-4">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Tech Stack Detection</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.company_dossier.estimated_tech_stack?.map(tech => (
                          <span key={tech} className="px-3 py-1 bg-brand-500/10 text-brand-300 rounded-lg text-xs border border-brand-500/20">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Strategy Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="glass rounded-3xl p-6 space-y-4">
                    <h4 className="flex items-center gap-2 text-white font-semibold">
                      <TrendingUp className="w-5 h-5 text-brand-400" />
                      Strategic Score
                    </h4>
                    <div className="flex items-center gap-4">
                      <div className="relative w-20 h-20">
                        <svg className="w-full h-full" viewBox="0 0 100 100">
                          <circle className="text-white/10 stroke-current" strokeWidth="8" fill="transparent" r="40" cx="50" cy="50" />
                          <motion.circle
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: result.verdict.score / 100 }}
                            transition={{ duration: 2 }}
                            className="text-brand-500 stroke-current" strokeWidth="8" strokeLinecap="round" fill="transparent" r="40" cx="50" cy="50"
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center font-bold text-xl text-white">
                          {result.verdict.score}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-bold text-gray-300">{result.strategic_analysis.why_now}</p>
                        <p className="text-xs text-gray-500 mt-1">{result.verdict.justification}</p>
                      </div>
                    </div>
                  </div>

                  <div className="glass rounded-3xl p-6 space-y-4">
                    <h4 className="flex items-center gap-2 text-white font-semibold">
                      <Mail className="w-5 h-5 text-brand-400" />
                      Target Persona
                    </h4>
                    <div className="space-y-3">
                      <div className="bg-white/5 p-3 rounded-2xl flex items-center justify-between">
                        <span className="text-gray-400 text-sm">Decision Maker</span>
                        <span className="text-brand-300 font-medium">{result.outreach_strategy.target_role}</span>
                      </div>
                      <p className="text-sm text-gray-400 leading-relaxed">
                        Strategy: Identifying {result.strategic_analysis.pain_points?.[0] || 'infrastructure'} inefficiencies.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Outreach Draft */}
                <div className="glass rounded-3xl p-8 glow-card overflow-hidden">
                  <div className="flex justify-between items-center mb-6">
                    <h4 className="flex items-center gap-2 text-white font-semibold">
                      <Send className="w-5 h-5 text-brand-400" />
                      Personalized Outreach Draft
                    </h4>
                    <button
                      onClick={() => copyToClipboard(result.outreach_strategy.custom_pitch)}
                      className="p-2 hover:bg-white/10 rounded-xl transition-all text-gray-400 hover:text-white"
                    >
                      <Copy className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="bg-black/20 p-6 rounded-2xl border border-white/5 group relative">
                    <div className="mb-4 pb-4 border-b border-white/5">
                      <span className="text-gray-500 text-sm">Subject:</span>
                      <span className="text-gray-300 text-sm ml-2 font-medium">{result.outreach_strategy.subject_line}</span>
                    </div>
                    <pre className="text-gray-300 font-sans whitespace-pre-wrap text-sm leading-relaxed">
                      {result.outreach_strategy.custom_pitch}
                    </pre>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-16 text-center text-gray-600 text-xs">
        &copy; 2026 DataVex AI — Autonomous Intelligence SDR Engine
      </footer>
    </div>
  );
}

export default App;
