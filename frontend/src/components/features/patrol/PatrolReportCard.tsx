import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Shield, CheckCircle, AlertTriangle, XCircle, Activity, ExternalLink, Search } from 'lucide-react';

interface PatrolCheck {
    name: string;
    data: any;
}

interface PatrolReport {
    timestamp: string;
    status: 'success' | 'warning' | 'failed';
    error?: string;
    checks: PatrolCheck[];
}

interface PatrolReportCardProps {
    report: PatrolReport;
}

const PatrolReportCard: React.FC<PatrolReportCardProps> = ({ report }) => {
    const [expanded, setExpanded] = useState(true);

    if (!report) return null;

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
            case 'failed': return <XCircle className="w-5 h-5 text-red-500" />;
            default: return <Activity className="w-5 h-5 text-gray-500" />;
        }
    };

    const statusColor = report.status === 'success' ? 'border-l-green-500' :
        report.status === 'warning' ? 'border-l-yellow-500' : 'border-l-red-500';

    return (
        <div className={`bg-gray-800 rounded-lg shadow-lg border-l-4 ${statusColor} mb-4 overflow-hidden max-w-2xl`}>
            {/* Header */}
            <div
                className="flex items-center justify-between p-4 bg-gray-900 cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-gray-100">每日巡检报告 (Patrol 2.0)</h3>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{new Date(report.timestamp).toLocaleString()}</span>
                    {getStatusIcon(report.status)}
                </div>
            </div>

            {/* Content */}
            {expanded && (
                <div className="p-4 space-y-4">
                    {report.error && (
                        <div className="p-3 bg-red-900/30 border border-red-700 rounded text-red-200 text-sm">
                            Error: {report.error}
                        </div>
                    )}

                    {report.checks.map((check, idx) => (
                        <div key={idx} className="border-b border-gray-700 pb-3 last:border-0">
                            <h4 className="text-sm font-medium text-blue-300 mb-2">{check.name}</h4>

                            {/* Render specific check types */}
                            {check.name === "Cluster Health" && (
                                <div className="text-sm">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-gray-400">Status:</span>
                                        <span className={check.data.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>
                                            {check.data.status.toUpperCase()}
                                        </span>
                                    </div>
                                    {check.data.not_ready_nodes && (
                                        <div className="text-red-400">
                                            ⚠️ Nodes Not Ready: {check.data.not_ready_nodes.join(', ')}
                                        </div>
                                    )}
                                </div>
                            )}

                            {check.name === "AI Diagnosis" && (
                                <div className="text-sm space-y-3">
                                    {check.data.issues?.length === 0 ? (
                                        <div className="text-green-400 flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4" /> No anomalies detected.
                                        </div>
                                    ) : (
                                        check.data.issues.map((issue: any, i: number) => (
                                            <div key={i} className="bg-gray-900/50 p-3 rounded border border-gray-700">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-red-400 font-bold">🔴 {issue.pod}</span>
                                                    {issue.report_id && (
                                                        <a
                                                            href={`http://localhost:8000/api/v1/patrol/visualize/${issue.report_id}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                                                        >
                                                            <Search className="w-3 h-3" /> View Evidence
                                                        </a>
                                                    )}
                                                </div>
                                                {issue.analysis ? (
                                                    <div className="space-y-1 text-gray-300">
                                                        <div className="flex gap-2">
                                                            <span className="bg-red-900/50 px-1 rounded text-xs text-red-300">{issue.analysis.incident_type}</span>
                                                            <span className="bg-gray-700 px-1 rounded text-xs text-gray-300">{issue.analysis.severity}</span>
                                                        </div>
                                                        <p><span className="text-gray-500">Cause:</span> {issue.analysis.root_cause}</p>
                                                        <p><span className="text-gray-500">Fix:</span> {issue.analysis.suggestion}</p>
                                                    </div>
                                                ) : (
                                                    <p className="text-xs text-gray-500 italic">AI Analysis failed to extract structure.</p>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default PatrolReportCard;
