import { formatNumber, formatRange, formatPercent } from '@/lib/utils';

describe('Utility Functions', () => {
  describe('formatNumber', () => {
    it('formats numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    it('handles null and undefined', () => {
      expect(formatNumber(null)).toBe('—');
      expect(formatNumber(undefined)).toBe('—');
    });

    it('handles zero', () => {
      expect(formatNumber(0)).toBe('0');
    });
  });

  describe('formatRange', () => {
    it('formats range with both min and max', () => {
      expect(formatRange(5, 12)).toBe('5–12');
      expect(formatRange(1, 10)).toBe('1–10');
    });

    it('formats range with only min', () => {
      expect(formatRange(5, null)).toBe('5–—');
    });

    it('formats range with only max', () => {
      expect(formatRange(null, 12)).toBe('—–12');
    });

    it('handles both null', () => {
      expect(formatRange(null, null)).toBe('—–—');
    });
  });

  describe('formatPercent', () => {
    it('formats percentages correctly', () => {
      expect(formatPercent(0.5)).toBe('50.0%');
      expect(formatPercent(0.75)).toBe('75.0%');
      expect(formatPercent(1.0)).toBe('100.0%');
      expect(formatPercent(0.0)).toBe('0.0%');
    });

    it('handles small decimals', () => {
      expect(formatPercent(0.01)).toBe('1.0%');
      expect(formatPercent(0.001)).toBe('0.1%');
    });
  });
});