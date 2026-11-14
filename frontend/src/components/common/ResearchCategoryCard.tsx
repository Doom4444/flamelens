import React from 'react';
import { ShieldAlert, Radio, Flame, ArrowRight, Compass } from 'lucide-react';
import { CategoryInfo } from '../../types';

interface ResearchCategoryCardProps {
  category: CategoryInfo;
  onExplore: (categoryId: string) => void;
}

export const ResearchCategoryCard: React.FC<ResearchCategoryCardProps> = ({
  category,
  onExplore,
}) => {
  const getIcon = () => {
    switch (category.id) {
      case 'prevention':
        return <ShieldAlert className="w-6 h-6 text-[#35C6E8]" />;
      case 'detection':
        return <Radio className="w-6 h-6 text-sky-400" />;
      case 'suppression':
        return <Flame className="w-6 h-6 text-[#FF914D]" />;
      default:
        return <Compass className="w-6 h-6 text-[#35C6E8]" />;
    }
  };

  const badgeColorClass = {
    prevention: 'bg-[#35C6E8]/10 text-[#35C6E8] border-[#35C6E8]/30',
    detection: 'bg-sky-400/10 text-sky-400 border-sky-400/30',
    suppression: 'bg-[#FF914D]/10 text-[#FF914D] border-[#FF914D]/30',
  }[category.id];

  return (
    <div className="flex flex-col justify-between p-6 rounded-lg bg-[#111E30] border border-[#243449] hover:border-[#334760] transition-all group">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="p-3 rounded-lg bg-[#0C1626] border border-[#243449]">
            {getIcon()}
          </div>
          <span className={`px-2.5 py-1 rounded text-xs font-mono font-medium border ${badgeColorClass}`}>
            CATEGORY 0{category.id === 'prevention' ? '1' : category.id === 'detection' ? '2' : '3'}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-[#F4F7FB] group-hover:text-[#35C6E8] transition-colors">
          {category.title}
        </h3>
        <p className="text-xs font-mono text-[#94A3B8] mt-0.5 mb-3">
          {category.subtitle}
        </p>

        <p className="text-sm text-[#94A3B8] leading-relaxed mb-4">
          {category.description}
        </p>

        <div className="mb-5">
          <p className="text-[11px] uppercase tracking-wider font-mono text-[#64748B] mb-2">
            Key NASA PSI Investigations
          </p>
          <div className="flex flex-wrap gap-1.5">
            {category.exampleInvestigations.map((inv) => (
              <span
                key={inv}
                className="px-2 py-0.5 rounded text-xs font-mono bg-[#0C1626] border border-[#243449] text-[#F4F7FB]"
              >
                {inv}
              </span>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={() => onExplore(category.id)}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-[#0C1626] border border-[#243449] hover:border-[#35C6E8] hover:text-[#35C6E8] text-sm font-medium text-[#F4F7FB] transition-all group-hover:bg-[#16253C]"
      >
        <span>Explore {category.title}</span>
        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
      </button>
    </div>
  );
};
