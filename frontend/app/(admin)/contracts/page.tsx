import { Eye, Pencil, Plus } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { contractScopeLabel, contractStatusLabel, contractStatusTone, contractStatuses } from "@/features/contracts/labels";
import { ResourceTable } from "@/features/resources/resource-table";
import { getContracts } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function ContractsPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; status?: string }>;
}) {
  const filters = await searchParams;
  const contracts = await getContracts(filters);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Hợp đồng</h1>
          <p className="mt-1 text-sm text-slate-500">
            Theo dõi lịch thuê phòng, nhà nguyên căn và công nợ theo hợp đồng.
          </p>
        </div>
        <Link href="/contracts/create">
          <Button type="button">
            <Plus className="size-4" />
            Thêm hợp đồng
          </Button>
        </Link>
      </div>

      <Card>
        <form className="grid gap-3 md:grid-cols-[minmax(0,1fr)_220px_auto]">
          <input
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.search ?? ""}
            name="search"
            placeholder="Tìm mã hợp đồng..."
          />
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.status ?? ""}
            name="status"
          >
            <option value="">Tất cả trạng thái</option>
            {contractStatuses.map(([value, label]) => (
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
            key: "contract_code",
            label: "Mã HĐ",
            render: (contract) => (
              <Link className="font-semibold text-ink hover:underline" href={`/contracts/${contract.id}`}>
                {contract.contract_code}
              </Link>
            ),
          },
          { key: "tenant_name", label: "Người thuê" },
          {
            key: "scope",
            label: "Tài sản",
            render: (contract) =>
              contract.scope === "whole_building"
                ? `${contractScopeLabel(contract.scope)} · ${contract.building_name ?? contract.building_id}`
                : `${contract.room_code ?? contract.room_id} · ${contract.building_name ?? contract.building_id}`,
          },
          { key: "start_date", label: "Bắt đầu" },
          { key: "end_date", label: "Kết thúc", render: (contract) => contract.end_date ?? "Không thời hạn" },
          { key: "monthly_rent", label: "Tiền thuê", render: (contract) => formatVnd(contract.monthly_rent) },
          {
            key: "status",
            label: "Trạng thái",
            render: (contract) => (
              <Badge tone={contractStatusTone(contract.status)}>{contractStatusLabel(contract.status)}</Badge>
            ),
          },
          {
            key: "actions",
            label: "",
            render: (contract) => (
              <div className="flex justify-end gap-2">
                <Link href={`/contracts/${contract.id}`} title={`Xem ${contract.contract_code}`}>
                  <Eye className="size-4" />
                </Link>
                <Link href={`/contracts/${contract.id}/edit`} title={`Sửa ${contract.contract_code}`}>
                  <Pencil className="size-4" />
                </Link>
              </div>
            ),
          },
        ]}
        items={contracts.items}
      />
    </div>
  );
}
