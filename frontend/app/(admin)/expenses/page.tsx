import { SimpleCreateForm } from "@/features/resources/simple-create-form";
import { ResourceTable } from "@/features/resources/resource-table";
import { getExpenses } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function ExpensesPage() {
  const expenses = await getExpenses();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thu chi</h1>
        <p className="mt-1 text-sm text-slate-500">Ghi nhận chi phí vận hành theo nhà và ngày phát sinh.</p>
      </div>
      <SimpleCreateForm
        endpoint="/expenses"
        fields={[
          { name: "building_id", label: "ID nhà", type: "number" },
          { name: "category", label: "Hạng mục" },
          { name: "amount", label: "Số tiền", type: "number" },
          { name: "spent_on", label: "Ngày chi", type: "date" },
        ]}
        title="Thêm chi phí"
      />
      <ResourceTable
        columns={[
          { key: "building_id", label: "Nhà" },
          { key: "category", label: "Hạng mục" },
          { key: "amount", label: "Số tiền", render: (expense) => formatVnd(expense.amount) },
          { key: "spent_on", label: "Ngày chi" },
        ]}
        items={expenses.items}
      />
    </div>
  );
}
