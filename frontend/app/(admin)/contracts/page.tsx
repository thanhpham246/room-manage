import { SimpleCreateForm } from "@/features/resources/simple-create-form";
import { ResourceTable, StatusBadge } from "@/features/resources/resource-table";
import { getContracts } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function ContractsPage() {
  const contracts = await getContracts();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Hợp đồng</h1>
        <p className="mt-1 text-sm text-slate-500">Theo dõi thuê phòng, tiền thuê và vòng đời hợp đồng.</p>
      </div>
      <SimpleCreateForm
        endpoint="/contracts"
        fields={[
          { name: "room_id", label: "ID phòng", type: "number" },
          { name: "tenant_id", label: "ID người thuê", type: "number" },
          { name: "start_date", label: "Ngày bắt đầu", type: "date" },
          { name: "end_date", label: "Ngày kết thúc", type: "date" },
          { name: "monthly_rent", label: "Tiền thuê", type: "number" },
          { name: "deposit_amount", label: "Tiền cọc", type: "number" },
        ]}
        title="Tạo hợp đồng"
      />
      <ResourceTable
        columns={[
          { key: "room_id", label: "Phòng" },
          { key: "tenant_id", label: "Người thuê" },
          { key: "monthly_rent", label: "Tiền thuê", render: (contract) => formatVnd(contract.monthly_rent) },
          { key: "status", label: "Trạng thái", render: (contract) => <StatusBadge status={contract.status} /> },
        ]}
        items={contracts.items}
      />
    </div>
  );
}
