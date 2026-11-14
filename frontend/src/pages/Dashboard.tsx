import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Flame,
  Search,
  Sparkles,
  Database,
  Layers,
  FileText,
  AlertTriangle,
  ArrowRight,
  HelpCircle,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { ResearchCategoryCard } from '../components/common/ResearchCategoryCard';
import { InvestigationCard } from '../components/common/InvestigationCard';
import { CategoryInfo, InvestigationPreview } from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Categories grounded in NASA PSI research areas
  const categories: CategoryInfo[] = [
    {
      id: 'prevention',
      title: 'Fire Prevention',
      subtitle: 'Materials Flammability & Extinction Limits',
      description:
        'Understanding how solid and gaseous materials ignite and propagate flames in microgravity to select spacecraft materials and establish safe atmospheric limits.',
      exampleInvestigations: ['BASS', 'BASS-II', 'Saffire-I through VI'],
      focusAreas: ['Ignition thresholds', 'Flame spread rates', 'Atmosphere composition'],
      accentColor: 'cyan',
    },
    {
      id: 'detection',
      title: 'Fire Detection',
      subtitle: 'Smoke Dynamics & Particulate Morphology',
      description:
        'Characterizing aerosol transport, smoke agglomerate sizes, and particulate behavior in the absence of buoyancy to engineer earlier, false-alarm-free detectors.',
      exampleInvestigations: ['SAME', 'SAME-R', 'DAFT'],
      focusAreas: ['Particle size distribution', 'Optical smoke sensing', 'Transport modeling'],
      accentColor: 'blue',
    },
    {
      id: 'suppression',
      title: 'Fire Suppression',
      subtitle: 'Droplet Combustion & Extinction Dynamics',
      description:
        'Analyzing suppressant dispersion, fuel droplet extinction diameters, and cool flame phenomena to develop effective non-toxic fire extinguishing mechanisms.',
      exampleInvestigations: ['FLEX', 'FLEX-2', 'ACME'],
      focusAreas: ['Extinction diameters', 'Cool flame regimes', 'Gaseous suppressants'],
      accentColor: 'orange',
    },
  ];

  // Representative illustrative investigations from NASA PSI repository
  const featuredInvestigations: InvestigationPreview[] = [
    {
      id: 'bass-ii',
      accessionId: 'PSI-BASS-II',
      title: 'Burning and Suppression of Solids - II (BASS-II)',
      category: 'prevention',
      description:
        'Examined the burning and extinction characteristics of a wide variety of fuel samples in microgravity to guide spacecraft material flammability standards and test methods.',
      facility: 'Microgravity Science Glovebox (MSG) / ISS',
      isIllustrative: true,
    },
    {
      id: 'same-r',
      accessionId: 'PSI-SAME-R',
      title: 'Smoke Aerosol Measurement Experiment - Reflight (SAME-R)',
      category: 'detection',
      description:
        'Measured the particulate size distribution of smoke produced from diverse spacecraft materials undergoing thermal degradation in microgravity to calibrate optical smoke detectors.',
      facility: 'International Space Station',
      isIllustrative: true,
    },
    {
      id: 'flex-2',
      accessionId: 'PSI-FLEX-2',
      title: 'Flame Extinguishment Experiment - 2 (FLEX-2)',
      category: 'suppression',
      description:
        'Investigated isolated and bi-component droplet combustion, radiative extinguishment, and cool flame behavior without buoyant convection.',
      facility: 'Combustion Integrated Rack (CIR) / ISS',
      isIllustrative: true,
    },
  ];

  const suggestedQuestions = [
    'Which experiments studied solid material flammability?',
    'What is the difference between FLEX and FLEX-2?',
    'Which research informs lunar habitat fire safety?',
    'What are the limitations of current microgravity combustion research?',
  ];

  return (
    <div className="space-y-10">
      {/* ==================================================================== */}
      {/* HERO / WELCOME SECTION */}
      {/* ==================================================================== */}
      <section className="relative overflow-hidden rounded-xl bg-gradient-to-br from-[#0C1626] via-[#111E30] to-[#080F1C] border border-[#243449] p-6 sm:p-8 lg:p-10 shadow-lg">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-[#35C6E8]/5 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 -mb-16 w-60 h-60 rounded-full bg-[#FF914D]/5 blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#080F1C]/80 border border-[#243449] text-xs font-mono text-[#35C6E8] mb-4">
            <Flame className="w-3.5 h-3.5 text-[#FF914D]" />
            <span>NASA Physical Sciences Informatics • Combustion Science</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#F4F7FB] font-sans">
            Flame<span className="text-[#35C6E8]">Lens</span>
          </h1>

          <p className="mt-3 text-lg sm:text-xl font-medium text-[#35C6E8]">
            Microgravity Combustion Intelligence for Safer Human Space Exploration.
          </p>

          <p className="mt-4 text-sm sm:text-base text-[#94A3B8] leading-relaxed">
            FlameLens aggregates and structures decades of NASA microgravity combustion
            investigations from the Physical Sciences Informatics (PSI) repository. By applying
            deterministic scientific parameter mapping, rigorous comparability analysis, and
            cited semantic retrieval, FlameLens accelerates fire safety engineering for the ISS,
            Artemis lunar habitats, and future deep-space missions.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              onClick={() => navigate('/investigations')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#35C6E8] hover:bg-[#35C6E8]/90 text-[#080F1C] font-semibold text-sm transition-all shadow-md shadow-[#35C6E8]/20"
            >
              <Search className="w-4 h-4" />
              <span>Explore Investigations</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => navigate('/assistant')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#111E30] hover:bg-[#16253C] text-[#F4F7FB] border border-[#243449] hover:border-[#35C6E8] font-medium text-sm transition-all"
            >
              <Sparkles className="w-4 h-4 text-[#35C6E8]" />
              <span>Ask AI Assistant</span>
            </button>
          </div>
        </div>
      </section>

      {/* ==================================================================== */}
      {/* RESEARCH SCOPE NOTICE (SCIENTIFIC ACCURACY) */}
      {/* ==================================================================== */}
      <div className="p-4 rounded-lg bg-[#111E30]/70 border border-[#243449] flex items-start gap-3.5">
        <div className="p-2 rounded bg-amber-400/10 border border-amber-400/20 text-amber-400 flex-shrink-0 mt-0.5">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div className="text-xs leading-relaxed text-[#94A3B8]">
          <span className="font-semibold text-[#F4F7FB] font-mono mr-1">
            RESEARCH SCOPE & DATA PROVENANCE NOTICE:
          </span>
          NASA Physical Sciences Informatics (PSI) currently provides microgravity ($\mu g$)
          combustion research conduct aboard orbital facilities (ISS, Space Shuttle, drop towers).
          Partial-gravity combustion datasets (e.g. Lunar $0.16g$, Martian $0.38g$) are not
          presently available according to challenge specifications. FlameLens strictly avoids
          fabricating or extrapolating unverified partial-gravity experimental values.
        </div>
      </div>

      {/* ==================================================================== */}
      {/* RESEARCH STATISTICS (METRICS READY FOR INGESTION) */}
      {/* ==================================================================== */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-[#F4F7FB]">Repository Telemetry</h2>
            <p className="text-xs text-[#94A3B8]">
              Live indexed inventory from NASA PSI Combustion Science
            </p>
          </div>
          <span className="text-xs font-mono text-[#64748B]">PHASE 1 FOUNDATION</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Investigations"
            value="--"
            description="Orbital & drop tower experiments"
            icon={Database}
            isPending={true}
            statusLabel="Data ingestion pending"
            accentColor="cyan"
          />
          <StatCard
            label="Research Categories"
            value="3"
            description="Prevention, Detection, Suppression"
            icon={Layers}
            isPending={false}
            accentColor="blue"
          />
          <StatCard
            label="Available Datasets"
            value="--"
            description="Numeric measurements & CSV series"
            icon={Flame}
            isPending={true}
            statusLabel="Data ingestion pending"
            accentColor="orange"
          />
          <StatCard
            label="Indexed Documents"
            value="--"
            description="Peer-reviewed papers & flight reports"
            icon={FileText}
            isPending={true}
            statusLabel="Data ingestion pending"
            accentColor="purple"
          />
        </div>
      </section>

      {/* ==================================================================== */}
      {/* RESEARCH CATEGORIES (FIRE SAFETY APPLICATIONS) */}
      {/* ==================================================================== */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-[#F4F7FB]">
              Space Exploration Fire Safety Domains
            </h2>
            <p className="text-xs text-[#94A3B8]">
              Primary mission applications for spacecraft and habitat safety architectures
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {categories.map((cat) => (
            <ResearchCategoryCard
              key={cat.id}
              category={cat}
              onExplore={(id) => navigate(`/investigations?category=${id}`)}
            />
          ))}
        </div>
      </section>

      {/* ==================================================================== */}
      {/* FEATURED RESEARCH (ILLUSTRATIVE PSI EXPERIMENTS) */}
      {/* ==================================================================== */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-[#F4F7FB]">
              Featured Microgravity Investigations
            </h2>
            <p className="text-xs text-[#94A3B8]">
              Key benchmark experiments illustrating core microgravity combustion phenomena
            </p>
          </div>
          <button
            onClick={() => navigate('/investigations')}
            className="text-xs font-mono text-[#35C6E8] hover:underline flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featuredInvestigations.map((inv) => (
            <InvestigationCard
              key={inv.id}
              investigation={inv}
              onViewDetails={(id) => navigate(`/investigations/${id}`)}
            />
          ))}
        </div>
      </section>

      {/* ==================================================================== */}
      {/* AI ASSISTANT ENTRY POINT */}
      {/* ==================================================================== */}
      <section className="rounded-xl bg-[#0C1626] border border-[#243449] p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-[#35C6E8]/10 text-[#35C6E8] text-xs font-mono mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>TRACEABLE SCIENTIFIC COPILOT</span>
            </div>
            <h3 className="text-xl font-bold text-[#F4F7FB]">
              Inquire with the FlameLens Scientific Assistant
            </h3>
            <p className="text-sm text-[#94A3B8] mt-1 max-w-2xl leading-relaxed">
              Query flight experiments, compare observed extinction limits, and understand
              differences in microgravity flame geometry with answers directly cited from
              published NASA investigations.
            </p>
          </div>

          <button
            onClick={() => navigate('/assistant')}
            className="flex-shrink-0 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#243449] hover:bg-[#334760] text-[#F4F7FB] hover:text-[#35C6E8] text-sm font-medium transition-colors"
          >
            <HelpCircle className="w-4 h-4 text-[#35C6E8]" />
            <span>Launch Assistant</span>
          </button>
        </div>

        <div>
          <p className="text-xs font-mono uppercase text-[#64748B] mb-3">
            Suggested Scientific Inquiries
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => navigate(`/assistant?query=${encodeURIComponent(q)}`)}
                className="text-left p-3 rounded-lg bg-[#111E30] border border-[#243449] hover:border-[#35C6E8] text-xs text-[#94A3B8] hover:text-[#F4F7FB] transition-all flex items-center justify-between group"
              >
                <span className="line-clamp-1">{q}</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#35C6E8] opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2" />
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};
