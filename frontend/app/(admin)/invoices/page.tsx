import { Receipt } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ResourceTable, StatusBadge } from "@/features/resources/resource-table";
import { getInvoices } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function InvoicesPage() {
  const invoices = await getInvoices();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Hóa đơn</h1>
          <p className="mt-1 text-sm text-slate-500">Tạo hóa đơn tháng sau khi nhập chỉ số điện nước.</p>
        </div>
        <Button type="button">
          <Receipt className="size-4" />
          Tạo hóa đơn tháng
        </Button>
      </div>
      <ResourceTable
        columns={[
          { key: "billing_month", label: "Tháng" },
          { key: "room_id", label: "Phòng" },
          { key: "total_amount", label: "Tổng tiền", render: (invoice) => formatVnd(invoice.total_amount) },
          { key: "paid_amount", label: "Đã trả", render: (invoice) => formatVnd(invoice.paid_amount) },
          { key: "status", label: "Trạng thái", render: (invoice) => <StatusBadge status={invoice.status} /> },
        ]}
        items={invoices.items}
      />
    </div>
  );
}
