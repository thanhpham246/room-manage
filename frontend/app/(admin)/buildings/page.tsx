import { Eye, Pencil, Plus } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { buildingStatusLabel, houseTypeLabel } from "@/features/buildings/labels";
import { ResourceTable } from "@/features/resources/resource-table";
import { getBuildings } from "@/lib/api/server";

export default async function BuildingsPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; house_type?: string; status?: string }>;
}) {
  const filters = await searchParams;
  const buildings = await getBuildings(filters);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Quản lý nhà</h1>
          <p className="mt-1 text-sm text-slate-500">Theo dõi danh sách tòa nhà đang vận hành.</p>
        </div>
        <Link href="/buildings/create">
          <Button type="button">
            <Plus className="size-4" />
            Thêm nhà
          </Button>
        </Link>
      </div>
      <Card>
        <form className="grid gap-3 md:grid-cols-[minmax(0,1fr)_180px_180px_auto]">
          <input
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.search ?? ""}
            name="search"
            placeholder="Tìm theo mã, tên, địa chỉ..."
          />
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.house_type ?? ""}
            name="house_type"
          >
            <option value="">Tất cả loại nhà</option>
            <option value="boarding_house">Nhà trọ</option>
            <option value="mini_apartment">Chung cư mini</option>
            <option value="dormitory">Ký túc xá</option>
            <option value="whole_house">Nhà nguyên căn</option>
          </select>
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.status ?? ""}
            name="status"
          >
            <option value="">Tất cả trạng thái</option>
            <option value="active">Đang hoạt động</option>
            <option value="temporarily_closed">Tạm đóng</option>
            <option value="under_renovation">Đang sửa chữa</option>
          </select>
          <Button type="submit" variant="secondary">
            Lọc
          </Button>
        </form>
      </Card>
      <ResourceTable
        columns={[
          { key: "code", label: "Mã nhà" },
          {
            key: "name",
            label: "Tên nhà",
            render: (building) => (
              <Link className="font-semibold text-ink hover:underline" href={`/buildings/${building.id}`}>
                {building.name}
              </Link>
            ),
          },
          { key: "house_type", label: "Loại", render: (building) => houseTypeLabel(building.house_type) },
          { key: "address", label: "Địa chỉ" },
          { key: "manager_name", label: "Quản lý" },
          {
            key: "total_rooms",
            label: "Phòng",
            render: (building) => `${building.occupied_rooms}/${building.total_rooms}`,
          },
          {
            key: "status",
            label: "Trạng thái",
            render: (building) => <Badge tone="green">{buildingStatusLabel(building.status)}</Badge>,
          },
          {
            key: "actions",
            label: "",
            render: (building) => (
              <div className="flex justify-end gap-2">
                <Link href={`/buildings/${building.id}`} title="Xem">
                  <Eye className="size-4" />
                </Link>
                <Link href={`/buildings/${building.id}/edit`} title="Sửa">
                  <Pencil className="size-4" />
                </Link>
              </div>
            ),
          },
        ]}
        items={buildings.items}
      />
    </div>
  );
}
