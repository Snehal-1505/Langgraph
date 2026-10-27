import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ReportViewer } from '../components/ReportViewer';
import { ReportRecord, SourceRecord } from '../types';

describe('ReportViewer Component', () => {
  const mockReport: ReportRecord = {
    id: 'rep_123',
    session_id: 'sess_123',
    version: 1,
    title: 'Impact of GenAI on Software Engineering',
    executive_summary: 'Generative AI accelerates velocity while introducing security and hallucination considerations.',
    markdown_content: '# Impact of GenAI on Software Engineering\n\n## 1. Executive Summary\nGenerative AI accelerates velocity.\n\n## 6. Key Findings\n- **Finding 1:** 25% velocity increase [1].\n\n## 12. References\n[1] [Empirical Benchmark](https://example.org) - Verified benchmark report.',
    review_status: 'passed',
    created_at: new Date().toISOString(),
  };

  const mockSources: SourceRecord[] = [
    {
      id: 'src_1',
      session_id: 'sess_123',
      url: 'https://example.org',
      title: 'Empirical Benchmark',
      domain: 'example.org',
      extracted_evidence: '25% velocity increase observed in field trials.',
      retrieval_timestamp: new Date().toISOString(),
      status: 'retrieved',
    },
  ];

  it('renders title, executive summary, and QC badge', () => {
    render(<ReportViewer report={mockReport} sources={mockSources} />);

    expect(screen.getAllByText('Impact of GenAI on Software Engineering').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Generative AI accelerates velocity while introducing security/i)).toBeInTheDocument();
    expect(screen.getByText(/QC Review: Approved/i)).toBeInTheDocument();
  });

  it('renders export buttons for Markdown and PDF', () => {
    render(<ReportViewer report={mockReport} sources={mockSources} />);

    expect(screen.getByText('.MD')).toBeInTheDocument();
    expect(screen.getByText('Export PDF')).toBeInTheDocument();
  });
});
