'use client';

import React from 'react';

interface SpeciesDetailProps {
  species: any;
}

export default function SpeciesDetail({ species }: any) {
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div>
          <h1>Test</h1>
          <span dir="rtl">Persian text</span>
        </div>
      </div>
    </div>
  );
}
