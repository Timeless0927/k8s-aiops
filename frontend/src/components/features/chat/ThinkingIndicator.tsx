import React from 'react';
import { Loader2, BrainCircuit } from 'lucide-react';

export const ThinkingIndicator: React.FC = () => {
    return (
        <div className="flex items-center gap-3 px-3 py-2 bg-white/80 border border-primary/20 rounded-full w-fit animate-pulse shadow-sm backdrop-blur-sm">
            <div className="flex h-4 w-4 items-center justify-center rounded-full bg-primary/10">
                <Loader2 className="h-3 w-3 animate-spin text-primary" />
            </div>
            <div className="flex flex-col gap-0 leading-none">
                <span className="text-[11px] font-semibold text-primary">深度思考中...</span>
            </div>
            <BrainCircuit className="ml-1 h-3.5 w-3.5 text-primary/40" />
        </div>
    );
};
