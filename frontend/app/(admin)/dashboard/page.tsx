import { Building2, CircleDollarSign, ClipboardCheck, Home } from "lucide-react";

import { Card } from "@/components/ui/card";
import { CashFlowChart } from "@/features/dashboard/cash-flow-chart";
import { getDashboardSummary } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

const kpiIcons = [CircleDollarSign, Building2, Home, ClipboardCheck];

export default async function DashboardPage() {
  const summary = await getDashboardSummary();
  const kpis = [
    {
      label: "Tổng thu tháng",
      value: formatVnd(summary.kpi.monthly_revenue),
      hint: "Doanh thu đã thanh toán",
    },
    {
      label: "Phòng đang thuê",
      value: `${summary.kpi.occupied_rooms} / ${summary.kpi.total_rooms}`,
      hint: "Tỷ lệ lấp đầy hiện tại",
    },
    {
      label: "Phòng trống",
      value: `${summary.kpi.vacant_rooms} phòng`,
      hint: "Cần tìm khách mới",
    },
    {
      label: "Công nợ",
      value: formatVnd(summary.kpi.outstanding_amount),
      hint: "Hóa đơn chưa thanh toán đủ",
    },
  ];

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-semibold tracking-normal text-ink">Xin chào, Chủ đầu tư</h1>
        <p className="mt-2 text-slate-500">
          Hôm nay bạn đang quản lý {summary.kpi.total_rooms} phòng trong hệ thống.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi, index) => {
          const Icon = kpiIcons[index];
          return (
            <Card className="min-h-36" key={kpi.label}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-500">{kpi.label}</p>
                  <p className="mt-8 text-2xl font-semibold text-ink">{kpi.value}</p>
                  <p className="mt-2 text-sm text-slate-500">{kpi.hint}</p>
                </div>
                <div className="flex size-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                  <Icon className="size-5" />
                </div>
              </div>
            </Card>
          );
        })}
      </section>
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <Card>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-ink">Dòng tiền</h2>
            <p className="text-sm text-slate-500">Thu thuê, chi phí và lợi nhuận theo tháng</p>
          </div>
          <CashFlowChart data={summary.cash_flow} />
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-ink">Tỷ lệ lấp đầy</h2>
          <div className="mt-10 flex flex-col items-center justify-center gap-6">
            <div className="flex size-52 items-center justify-center rounded-full border-[26px] border-emerald-400">
              <div className="text-center">
                <p className="text-2xl font-semibold text-ink">
                  {summary.kpi.total_rooms === 0
                    ? 0
                    : Math.round((summary.kpi.occupied_rooms / summary.kpi.total_rooms) * 100)}
                  %
                </p>
                <p className="text-sm text-slate-500">Đang thuê</p>
              </div>
            </div>
            <p className="text-sm text-slate-500">
              {summary.kpi.occupied_rooms} phòng đang thuê, {summary.kpi.vacant_rooms} phòng trống
            </p>
          </div>
        </Card>
      </section>
    </div>
  );
}
