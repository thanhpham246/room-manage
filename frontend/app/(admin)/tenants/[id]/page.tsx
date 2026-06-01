import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { genderLabel, identityTypeLabel, tenantStatusLabel, tenantStatusTone } from "@/features/tenants/labels";
import { TenantDeleteButton } from "@/features/tenants/tenant-delete-button";
import { getTenant } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function TenantDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const tenant = await getTenant(Number(id));
  if (!tenant) {
    notFound();
  }

  const kpis = [
    { label: "Trạng thái", value: tenantStatusLabel(tenant.status) },
    { label: "Tiền cọc đang giữ", value: formatVnd(tenant.deposit_amount) },
    { label: "Công nợ", value: formatVnd(tenant.current_debt) },
    { label: "Hóa đơn chưa thanh toán", value: String(tenant.unpaid_invoices) },
    { label: "Đã thanh toán", value: formatVnd(tenant.total_paid) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-ink"
            href="/tenants"
          >
            <ArrowLeft className="size-4" />
            Quay lại danh sách
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-ink">{tenant.full_name}</h1>
            <Badge tone={tenantStatusTone(tenant.status)}>{tenantStatusLabel(tenant.status)}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {tenant.tenant_code} · {tenant.phone}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href={`/tenants/${tenant.id}/edit`}>
            <Button type="button" variant="secondary">
              <Pencil className="size-4" />
              Sửa
            </Button>
          </Link>
          {tenant.status !== "deleted" ? <TenantDeleteButton tenantId={tenant.id} /> : null}
        </div>
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
          <h2 className="text-lg font-semibold text-ink">Hồ sơ cá nhân</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Info label="Email" value={tenant.email ?? "Chưa khai báo"} />
            <Info label="Zalo" value={tenant.zalo ?? "Chưa khai báo"} />
            <Info label="Ngày sinh" value={tenant.date_of_birth ?? "Chưa khai báo"} />
            <Info label="Giới tính" value={genderLabel(tenant.gender)} />
            <Info label="Loại giấy tờ" value={identityTypeLabel(tenant.identity_type)} />
            <Info label="Số giấy tờ" value={tenant.identity_number ?? "Chưa khai báo"} />
            <Info label="Ngày cấp" value={tenant.identity_issued_date ?? "Chưa khai báo"} />
            <Info label="Nơi cấp" value={tenant.identity_issued_place ?? "Chưa khai báo"} />
            <Info label="Địa chỉ thường trú" value={tenant.permanent_address ?? "Chưa khai báo"} />
            <Info label="Địa chỉ hiện tại" value={tenant.current_address ?? "Chưa khai báo"} />
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-ink">Tình trạng thuê</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Info
              label="Nhà hiện tại"
              value={tenant.current_building_name ?? "Chưa có"}
              href={tenant.current_building_id ? `/buildings/${tenant.current_building_id}` : undefined}
            />
            <Info
              label="Phòng hiện tại"
              value={tenant.current_room_code ?? "Chưa có"}
              href={tenant.current_room_id ? `/rooms/${tenant.current_room_id}` : undefined}
            />
            <Info label="Hợp đồng hiện tại" value={tenant.active_contract_id ? `#${tenant.active_contract_id}` : "Chưa có"} />
            <Info label="Ngày bắt đầu" value={tenant.contract_start_date ?? "Chưa có"} />
            <Info label="Ngày kết thúc" value={tenant.contract_end_date ?? "Chưa có"} />
            <Info label="Thanh toán gần nhất" value={tenant.last_payment_date ?? "Chưa có"} />
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-ink">Liên hệ khẩn cấp</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Info label="Người liên hệ" value={tenant.emergency_contact_name ?? "Chưa khai báo"} />
            <Info label="Số điện thoại" value={tenant.emergency_contact_phone ?? "Chưa khai báo"} />
            <Info label="Quan hệ" value={tenant.emergency_contact_relationship ?? "Chưa khai báo"} />
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-ink">Ghi chú</h2>
          <p className="mt-4 whitespace-pre-wrap text-sm text-slate-600">
            {tenant.note || "Chưa có ghi chú"}
          </p>
        </Card>
      </section>
    </div>
  );
}

function Info({ href, label, value }: { href?: string; label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      {href ? (
        <Link className="mt-1 block font-medium text-ink hover:underline" href={href}>
          {value}
        </Link>
      ) : (
        <p className="mt-1 font-medium text-ink">{value}</p>
      )}
    </div>
  );
}
