import { SimpleCreateForm } from "@/features/resources/simple-create-form";
import { ResourceTable, StatusBadge } from "@/features/resources/resource-table";
import { getPayments } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function PaymentsPage() {
  const payments = await getPayments();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thanh toán</h1>
        <p className="mt-1 text-sm text-slate-500">Ghi nhận thanh toán một phần hoặc toàn bộ hóa đơn.</p>
      </div>
      <SimpleCreateForm
        endpoint="/payments"
        fields={[
          { name: "invoice_id", label: "ID hóa đơn", type: "number" },
          { name: "amount", label: "Số tiền", type: "number" },
          { name: "method", label: "Phương thức" },
        ]}
        title="Ghi nhận thanh toán"
      />
      <ResourceTable
        columns={[
          { key: "invoice_id", label: "Hóa đơn" },
          { key: "amount", label: "Số tiền", render: (payment) => formatVnd(payment.amount) },
          { key: "method", label: "Phương thức" },
          { key: "invoice_status", label: "Trạng thái", render: (payment) => <StatusBadge status={payment.invoice_status} /> },
        ]}
        items={payments.items}
      />
    </div>
  );
}
