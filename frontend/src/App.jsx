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
  ChevronDown,
  Loader2,
  Copy,
  Zap,
  Globe,
  Building,
  Activity,
  Briefcase
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SERVICE_CATEGORIES = [
  'Application Development',
  'AI & Data Analytics',
  'Cloud & DevOps',
  'Digital Transformation'
];

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [mode, setMode] = useState('campaign'); // 'campaign' or 'single'
  const [domain, setDomain] = useState('');
  const [serviceCategory, setServiceCategory] = useState('Application Development');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [trace, setTrace] = useState([]);
  const [emails, setEmails] = useState({});
  const [emailLoading, setEmailLoading] = useState({});
  const traceEndRef = useRef(null);

  const scrollToBottom = () => {
    traceEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [trace]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (mode === 'single' && !domain.trim()) {
      setError("Please enter a valid domain (e.g., example.com)");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setTrace(["Initializing autonomous intelligence engine..."]);

    try {
      let res;
      if (mode === 'campaign') {
        res = await axios.post(`${API_BASE_URL}/analyze`, {
          service_category: serviceCategory
        });
      } else {
        res = await axios.post(`${API_BASE_URL}/deep_analyze`, {
          domain: domain,
          service_category: serviceCategory
        });
      }

      // Simulate steps for better UX
      for (const step of res.data.agent_trace) {
        setTrace(prev => [...prev, step]);
        await new Promise(r => setTimeout(r, 600)); // slightly faster
      }

      setResult({ ...res.data, mode });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to execute request. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateEmail = async (lead, index) => {
    setEmailLoading(prev => ({ ...prev, [index]: true }));
    try {
      const res = await axios.post(`${API_BASE_URL}/generate_email`, {
        company_name: lead.name,
        domain: lead.domain,
        why_we_help: lead.why_we_help,
        service_category: serviceCategory
      });
      setEmails(prev => ({ ...prev, [index]: res.data.email_body }));
    } catch (err) {
      console.error("Failed to generate email:", err);
      alert("Failed to generate email. Is the backend running?");
    } finally {
      setEmailLoading(prev => ({ ...prev, [index]: false }));
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  // Rendering for the campaign results
  const renderCampaignResults = () => {
    if (!result.leads || result.leads.length === 0) {
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="h-full min-h-[400px] glass rounded-3xl border-dashed border-red-500/20 flex flex-col items-center justify-center text-red-400/80 p-8 text-center"
        >
          <XCircle className="w-12 h-12 mb-4 opacity-50" />
          <p>No valid SMB leads found for this category right now.</p>
        </motion.div>
      );
    }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-6"
      >
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-bold text-white">Recommended Leads</h3>
          <span className="bg-brand-500/10 text-brand-400 border border-brand-500/20 px-3 py-1 rounded-full text-sm font-medium">
            {result.leads.length} found
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {result.leads.map((lead, idx) => (
            <div key={idx} className="glass rounded-2xl p-6 glow-card transition-all hover:border-brand-500/30">
              {/* Similar to existing lead display */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-xl font-bold text-white flex items-center gap-2">
                    {lead.name}
                  </h4>
                  <a
                    href={`https://${lead.domain}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-brand-400 text-sm hover:underline mt-1 inline-block"
                  >
                    {lead.domain}
                  </a>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleGenerateEmail(lead, idx)}
                    disabled={emailLoading[idx]}
                    className="flex items-center gap-2 px-3 py-1.5 bg-brand-500/20 hover:bg-brand-500/30 text-brand-300 rounded-xl transition-all font-medium text-sm disabled:opacity-50"
                  >
                    {emailLoading[idx] ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                    {emails[idx] ? "Regenerate Email" : "Draft Email"}
                  </button>
                  <button
                    onClick={() => copyToClipboard(lead.why_we_help)}
                    className="p-2 hover:bg-white/10 rounded-xl transition-all text-gray-400 hover:text-white"
                    title="Copy strategy"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 p-4 rounded-xl mb-4">
                <span className="text-xs uppercase tracking-wider text-gray-500 font-bold block mb-2">Why they need DataVex</span>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {lead.why_we_help}
                </p>
              </div>

              <AnimatePresence>
                {emails[idx] && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-brand-950/30 border border-brand-500/20 p-4 rounded-xl relative overflow-hidden mt-4"
                  >
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-xs uppercase tracking-wider text-brand-400 font-bold flex items-center gap-2">
                        <Send className="w-3 h-3" /> AI Drafted Email
                      </span>
                      <button
                        onClick={() => copyToClipboard(emails[idx])}
                        className="flex items-center gap-1 text-xs text-brand-300 hover:text-white bg-brand-500/20 hover:bg-brand-500/40 px-2 py-1 rounded transition-colors"
                      >
                        <Copy className="w-3 h-3" /> Copy Email
                      </button>
                    </div>
                    <div className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed font-mono">
                      {emails[idx]}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </motion.div>
    );
  };

  // Rendering for single domain deep analysis results
  const renderSingleDomainResults = () => {
    const { company_dossier, strategic_analysis, verdict, outreach_strategy } = result;

    if (!company_dossier) return null;

    const isYes = verdict?.recommendation === "YES";
    const scoreColor = verdict?.score >= 60 ? 'text-green-400' : (verdict?.score >= 35 ? 'text-yellow-400' : 'text-red-400');

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-6"
      >
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-bold text-white">Deep Analysis Report</h3>
          <span className="text-gray-400 text-xs font-mono">{company_dossier.analysis_timestamp}</span>
        </div>

        {/* Verdict Banner */}
        <div className={`glass rounded-2xl p-6 border-l-4 ${isYes ? 'border-l-green-500' : 'border-l-red-500'}`}>
          <div className="flex justify-between items-start mb-4">
            <div>
              <h4 className="text-2xl font-bold text-white mb-1 flex items-center gap-3">
                {isYes ? <CheckCircle2 className="w-6 h-6 text-green-400" /> : <XCircle className="w-6 h-6 text-red-400" />}
                Verdict: {verdict?.recommendation}
              </h4>
              <p className="text-gray-300 text-sm mt-2">{verdict?.justification}</p>
            </div>
            <div className="text-center bg-white/5 px-4 py-2 rounded-xl">
              <span className={`text-3xl font-black ${scoreColor}`}>
                {verdict?.score}
              </span>
              <span className="block text-xs text-gray-400 uppercase tracking-widest mt-1">Score</span>
            </div>
          </div>
          <div className="inline-block px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-xs font-medium text-gray-300">
            Size Flag: <span className="text-gray-100">{verdict?.size_flag}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Dossier */}
          <div className="glass rounded-2xl p-6">
            <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2 border-b border-white/10 pb-3">
              <Building className="w-4 h-4 text-brand-400" />
              Company Dossier
            </h4>
            <div className="space-y-4">
              <div>
                <span className="text-xs text-brand-300 font-bold uppercase tracking-wider block mb-1">Company Info</span>
                <p className="text-white text-lg font-medium">{company_dossier.title}</p>
                <a href={`https://${company_dossier.domain}`} target="_blank" rel="noreferrer" className="text-gray-400 text-sm hover:underline">{company_dossier.domain}</a>
              </div>
              <p className="text-sm text-gray-300 leading-relaxed bg-white/5 p-3 rounded-lg border border-white/5">
                {company_dossier.summary}
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider block mb-1">Industry</span>
                  <p className="text-gray-200 text-sm">{company_dossier.industry}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider block mb-1">Stage</span>
                  <p className="text-gray-200 text-sm">{company_dossier.company_stage}</p>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-gray-500 uppercase tracking-wider block mb-1">Size Estimate</span>
                  <p className="text-gray-200 text-sm">{company_dossier.company_size}</p>
                </div>
              </div>
              {company_dossier.estimated_tech_stack?.length > 0 && (
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider block mb-2">Tech Stack Indications</span>
                  <div className="flex flex-wrap gap-2">
                    {company_dossier.estimated_tech_stack.map((tech, i) => (
                      <span key={i} className="px-2 py-1 bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs rounded-md">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Strategic Analysis */}
          <div className="glass rounded-2xl p-6">
            <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2 border-b border-white/10 pb-3">
              <Activity className="w-4 h-4 text-brand-400" />
              Strategic Analysis
            </h4>
            <div className="space-y-5">
              <div>
                <span className="text-xs text-brand-300 font-bold uppercase tracking-wider block mb-2">Why Now?</span>
                <p className="text-sm text-gray-300">{strategic_analysis?.why_now}</p>
              </div>
              <div>
                <span className="text-xs text-brand-300 font-bold uppercase tracking-wider block mb-2">Pain Points</span>
                <ul className="list-disc pl-4 text-sm text-gray-300 space-y-1">
                  {strategic_analysis?.pain_points?.map((pain, i) => (
                    <li key={i}>{pain}</li>
                  ))}
                  {(!strategic_analysis?.pain_points || strategic_analysis?.pain_points.length === 0) && (
                    <li className="text-gray-500 list-none -ml-4">None identified</li>
                  )}
                </ul>
              </div>
              <div>
                <span className="text-xs text-brand-300 font-bold uppercase tracking-wider block mb-2">DataVex Match</span>
                <p className="text-sm text-white font-medium bg-brand-500/20 border border-brand-500/30 p-3 rounded-xl">
                  {strategic_analysis?.datavex_service_match}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Outreach Strategy */}
        <div className="glass rounded-2xl p-6">
          <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-3">
            <h4 className="text-lg font-semibold text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-400" />
              Outreach Strategy
            </h4>
          </div>
          <div className="grid grid-cols-1 gap-4">
            <div className="flex items-center gap-4 text-sm text-gray-300">
              <span className="font-bold text-gray-400">Target Role:</span> {outreach_strategy?.target_role}
            </div>
            {outreach_strategy?.subject_line && outreach_strategy?.subject_line !== "N/A" && (
              <div className="flex items-center gap-4 text-sm text-gray-300">
                <span className="font-bold text-gray-400">Subject Line:</span> {outreach_strategy?.subject_line}
              </div>
            )}
            <div className="bg-brand-950/40 border border-brand-500/20 p-4 rounded-xl relative mt-2">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs uppercase tracking-wider text-brand-400 font-bold flex items-center gap-2">
                  <Send className="w-3 h-3" /> Custom Pitch Fragment
                </span>
                <button
                  onClick={() => copyToClipboard(outreach_strategy?.custom_pitch)}
                  className="flex items-center gap-1 text-xs text-brand-300 hover:text-white bg-brand-500/20 hover:bg-brand-500/40 px-2 py-1 rounded transition-colors"
                >
                  <Copy className="w-3 h-3" /> Copy
                </button>
              </div>
              <div className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed italic">
                "{outreach_strategy?.custom_pitch}"
              </div>
            </div>
          </div>
        </div>

      </motion.div>
    );
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
            DataVex <span className="text-brand-400">Intelligence</span>
          </h1>
        </motion.div>
        <p className="text-gray-400 text-center max-w-xl">
          Beyond the search bar. Our autonomous agents research pivots, tech debt, and fiscal pressures to find your next enterprise partner.
        </p>
      </header>

      <main className={`max-w-7xl mx-auto grid grid-cols-1 gap-8 items-start ${mode === 'campaign' ? 'lg:grid-cols-12' : ''}`}>
        {/* Input & Trace Column */}
        <div className={`space-y-6 ${mode === 'campaign' ? 'lg:col-span-5' : 'max-w-4xl mx-auto w-full'}`}>
          <section className="glass rounded-3xl p-8 glow-card">

            {/* Mode Switcher */}
            <div className="flex gap-4 mb-8">
              <button
                type="button"
                onClick={() => setMode('campaign')}
                className={`flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 font-semibold transition-all ${mode === 'campaign' ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20' : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'}`}
              >
                <Search className="w-4 h-4" />
                Find Leads
              </button>
              <button
                type="button"
                onClick={() => setMode('single')}
                className={`flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 font-semibold transition-all ${mode === 'single' ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20' : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'}`}
              >
                <Target className="w-4 h-4" />
                Deep Analyze
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <AnimatePresence mode="popLayout">
                {mode === 'single' && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-4 mb-4"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Target Domain</label>
                      <div className="relative group">
                        <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-brand-400 w-5 h-5 transition-colors" />
                        <input
                          type="text"
                          placeholder="e.g. example.com"
                          value={domain}
                          onChange={(e) => setDomain(e.target.value)}
                          disabled={loading}
                          className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-500/50 transition-all"
                          required
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="space-y-4">
                {mode === 'campaign' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Target Service to Pitch</label>
                    <div className="relative group">
                      <Cpu className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-brand-400 w-5 h-5 transition-colors" />
                      <select
                        value={serviceCategory}
                        onChange={(e) => setServiceCategory(e.target.value)}
                        disabled={loading}
                        className="w-full appearance-none bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-12 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 transition-all cursor-pointer"
                      >
                        {SERVICE_CATEGORIES.map(category => (
                          <option key={category} value={category} className="bg-gray-900 text-white">
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-600 hover:bg-brand-500 active:scale-[0.98] disabled:opacity-50 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 transition-all shadow-xl shadow-brand-600/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Autonomous Search Active...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    {mode === 'campaign' ? "Find SMB Leads" : "Run Intelligence Scan"}
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
          {(trace.length > 0 || mode === 'campaign') && (
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
          )}
        </div>

        {/* Results Column */}
        <div className={mode === 'campaign' ? 'lg:col-span-7 space-y-6' : 'max-w-4xl mx-auto w-full'}>
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full min-h-[400px] glass rounded-3xl border-dashed border-white/10 flex flex-col items-center justify-center text-gray-500 p-8"
              >
                <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                  <Cpu className="w-8 h-8 opacity-20" />
                </div>
                <p>Awaiting Autonomous Analysis</p>
              </motion.div>
            ) : result.mode === 'campaign' ? (
              renderCampaignResults()
            ) : (
              renderSingleDomainResults()
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-16 text-center text-gray-600 text-xs pb-8">
        &copy; 2026 DataVex AI — Autonomous Intelligence SDR Engine
      </footer>
    </div>
  );
}

export default App;