"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { formatVnd } from "@/lib/formatters/currency";

type CashFlowPoint = {
  month: string;
  revenue: number;
  expenses: number;
  profit: number;
};

export function CashFlowChart({ data }: { data: CashFlowPoint[] }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => setMounted(true));
    return () => window.cancelAnimationFrame(frame);
  }, []);

  return (
    <div className="h-80 w-full">
      {mounted ? (
        <ResponsiveContainer height="100%" minWidth={0} width="100%">
          <AreaChart data={data} margin={{ left: 4, right: 12, top: 20 }}>
            <defs>
              <linearGradient id="revenue" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
            <XAxis dataKey="month" tickLine={false} />
            <YAxis tickFormatter={(value) => `${Number(value) / 1000000}M`} tickLine={false} />
            <Tooltip formatter={(value) => formatVnd(Number(value))} />
            <Area
              dataKey="revenue"
              fill="url(#revenue)"
              name="Doanh thu"
              stroke="#10b981"
              strokeWidth={2}
              type="monotone"
            />
            <Area
              dataKey="expenses"
              fill="transparent"
              name="Chi phí"
              stroke="#f59e0b"
              strokeDasharray="5 5"
              strokeWidth={2}
              type="monotone"
            />
            <Area
              dataKey="profit"
              fill="transparent"
              name="Lợi nhuận"
              stroke="#334155"
              strokeWidth={2}
              type="monotone"
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : null}
    </div>
  );
}
