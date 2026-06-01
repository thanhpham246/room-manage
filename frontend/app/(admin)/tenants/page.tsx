import { Eye, Pencil, Plus } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ResourceTable } from "@/features/resources/resource-table";
import { tenantStatusLabel, tenantStatusTone, tenantStatuses } from "@/features/tenants/labels";
import { getTenants } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function TenantsPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; status?: string; include_deleted?: string }>;
}) {
  const filters = await searchParams;
  const tenants = await getTenants(filters);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Người thuê</h1>
          <p className="mt-1 text-sm text-slate-500">Quản lý hồ sơ, liên hệ và trạng thái thuê.</p>
        </div>
        <Link href="/tenants/create">
          <Button type="button">
            <Plus className="size-4" />
            Thêm người thuê
          </Button>
        </Link>
      </div>

      <Card>
        <form className="grid gap-3 md:grid-cols-[minmax(0,1fr)_220px_auto]">
          <input
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.search ?? ""}
            name="search"
            placeholder="Tìm mã, tên, SĐT, email, CCCD..."
          />
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.status ?? ""}
            name="status"
          >
            <option value="">Tất cả trạng thái</option>
            {tenantStatuses.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <Button type="submit" variant="secondary">
            Lọc
          </Button>
        </form>
      </Card>

      <ResourceTable
        columns={[
          {
            key: "tenant_code",
            label: "Mã",
            render: (tenant) => (
              <Link className="font-semibold text-ink hover:underline" href={`/tenants/${tenant.id}`}>
                {tenant.tenant_code}
              </Link>
            ),
          },
          { key: "full_name", label: "Họ tên" },
          { key: "phone", label: "SĐT" },
          { key: "email", label: "Email" },
          {
            key: "current_room_code",
            label: "Phòng hiện tại",
            render: (tenant) => tenant.current_room_code ?? "Chưa có",
          },
          {
            key: "current_building_name",
            label: "Nhà",
            render: (tenant) => tenant.current_building_name ?? "Chưa có",
          },
          {
            key: "current_debt",
            label: "Công nợ",
            render: (tenant) => formatVnd(tenant.current_debt),
          },
          {
            key: "status",
            label: "Trạng thái",
            render: (tenant) => (
              <Badge tone={tenantStatusTone(tenant.status)}>{tenantStatusLabel(tenant.status)}</Badge>
            ),
          },
          {
            key: "actions",
            label: "",
            render: (tenant) => (
              <div className="flex justify-end gap-2">
                <Link href={`/tenants/${tenant.id}`} title={`Xem ${tenant.tenant_code}`}>
                  <Eye className="size-4" />
                </Link>
                <Link href={`/tenants/${tenant.id}/edit`} title={`Sửa ${tenant.tenant_code}`}>
                  <Pencil className="size-4" />
                </Link>
              </div>
            ),
          },
        ]}
        items={tenants.items}
      />
    </div>
  );
}
