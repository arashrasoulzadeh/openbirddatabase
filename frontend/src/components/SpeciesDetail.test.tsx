'use client';

import React from 'react';
import { Species } from '@/lib/types';

interface SpeciesDetailProps {
  species: any;
}

export default function SpeciesDetail({ species }: SpeciesDetailProps) {
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div>Test</div>
      </div>
    </div>
  );
}
