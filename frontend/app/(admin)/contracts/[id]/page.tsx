import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { contractScopeLabel, contractStatusLabel, contractStatusTone } from "@/features/contracts/labels";
import { getContract } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function ContractDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const contract = await getContract(Number(id));
  if (!contract) {
    notFound();
  }

  const assetLabel =
    contract.scope === "whole_building"
      ? `${contractScopeLabel(contract.scope)} · ${contract.building_name ?? contract.building_id}`
      : `${contract.room_code ?? contract.room_id} · ${contract.building_name ?? contract.building_id}`;
  const kpis = [
    { label: "Tiền thuê", value: formatVnd(contract.monthly_rent) },
    { label: "Tiền cọc", value: formatVnd(contract.deposit_amount) },
    { label: "Đã lập hóa đơn", value: formatVnd(contract.total_invoiced) },
    { label: "Đã thanh toán", value: formatVnd(contract.total_paid) },
    { label: "Công nợ", value: formatVnd(contract.outstanding_amount) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-ink"
            href="/contracts"
          >
            <ArrowLeft className="size-4" />
            Quay lại danh sách
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-ink">{contract.contract_code}</h1>
            <Badge tone={contractStatusTone(contract.status)}>{contractStatusLabel(contract.status)}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-500">{assetLabel}</p>
        </div>
        <Link href={`/contracts/${contract.id}/edit`}>
          <Button type="button" variant="secondary">
            <Pencil className="size-4" />
            Sửa
          </Button>
        </Link>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {kpis.map((kpi) => (
          <Card className="min-h-28" key={kpi.label}>
            <p className="text-sm text-slate-500">{kpi.label}</p>
            <p className="mt-6 text-2xl font-semibold text-ink">{kpi.value}</p>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h2 className="text-lg font-semibold text-ink">Thông tin thuê</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Info label="Người thuê" value={contract.tenant_name ?? `#${contract.tenant_id}`} />
            <Info label="Loại tài sản" value={contractScopeLabel(contract.scope)} />
            <Info label="Nhà" value={contract.building_name ?? `#${contract.building_id}`} />
            <Info label="Phòng" value={contract.room_code ?? "Không áp dụng"} />
            <Info label="Ngày bắt đầu" value={contract.start_date} />
            <Info label="Ngày kết thúc" value={contract.end_date ?? "Không thời hạn"} />
          </div>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-ink">Ghi chú</h2>
          <p className="mt-4 whitespace-pre-wrap text-sm text-slate-600">
            {contract.note || "Chưa có ghi chú"}
          </p>
        </Card>
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 font-medium text-ink">{value}</p>
    </div>
  );
}
