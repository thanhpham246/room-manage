import { Eye, Pencil, Plus } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ResourceTable } from "@/features/resources/resource-table";
import { roomStatusLabel, roomStatusTone, roomTypeLabel, roomStatuses, roomTypes } from "@/features/rooms/labels";
import { getBuildings, getBuildingTree, getRooms } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function RoomsPage({
  searchParams,
}: {
  searchParams: Promise<{
    building_id?: string;
    floor_id?: string;
    status?: string;
    room_type?: string;
    search?: string;
  }>;
}) {
  const filters = await searchParams;
  const [rooms, buildings] = await Promise.all([getRooms(filters), getBuildings()]);
  const selectedBuildingId = filters.building_id ? Number(filters.building_id) : null;
  const selectedTree = selectedBuildingId ? await getBuildingTree(selectedBuildingId) : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Quản lý phòng</h1>
          <p className="mt-1 text-sm text-slate-500">
            Theo dõi phòng theo nhà, tầng, trạng thái và công nợ.
          </p>
        </div>
        <Link href="/rooms/create">
          <Button type="button">
            <Plus className="size-4" />
            Thêm phòng
          </Button>
        </Link>
      </div>

      <Card>
        <form className="grid gap-3 md:grid-cols-[minmax(0,1fr)_180px_160px_160px_160px_auto]">
          <input
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.search ?? ""}
            name="search"
            placeholder="Tìm mã hoặc tên phòng..."
          />
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.building_id ?? ""}
            name="building_id"
          >
            <option value="">Tất cả nhà</option>
            {buildings.items.map((building) => (
              <option key={building.id} value={building.id}>
                {building.name}
              </option>
            ))}
          </select>
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.floor_id ?? ""}
            disabled={!selectedTree}
            name="floor_id"
          >
            <option value="">Tất cả tầng</option>
            {selectedTree?.floors.map((floor) => (
              <option key={floor.id} value={floor.id}>
                {floor.name}
              </option>
            ))}
          </select>
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.status ?? ""}
            name="status"
          >
            <option value="">Tất cả trạng thái</option>
            {roomStatuses.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select
            className="h-10 rounded-md border border-border px-3 text-sm"
            defaultValue={filters.room_type ?? ""}
            name="room_type"
          >
            <option value="">Tất cả loại</option>
            {roomTypes.map(([value, label]) => (
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
            key: "code",
            label: "Mã phòng",
            render: (room) => (
              <Link className="font-semibold text-ink hover:underline" href={`/rooms/${room.id}`}>
                {room.code}
              </Link>
            ),
          },
          { key: "name", label: "Tên phòng" },
          {
            key: "building_name",
            label: "Nhà / tầng",
            render: (room) => `${room.building_name ?? room.building_id} / ${room.floor_name ?? "-"}`,
          },
          { key: "room_type", label: "Loại", render: (room) => roomTypeLabel(room.room_type) },
          {
            key: "status",
            label: "Trạng thái",
            render: (room) => (
              <Badge tone={roomStatusTone(room.status)}>{roomStatusLabel(room.status)}</Badge>
            ),
          },
          { key: "rent_price", label: "Giá thuê", render: (room) => formatVnd(room.rent_price) },
          { key: "deposit_amount", label: "Cọc", render: (room) => formatVnd(room.deposit_amount) },
          { key: "current_tenant_name", label: "Người thuê" },
          { key: "current_debt", label: "Công nợ", render: (room) => formatVnd(room.current_debt) },
          {
            key: "actions",
            label: "",
            render: (room) => (
              <div className="flex justify-end gap-2">
                <Link href={`/rooms/${room.id}`} title={`Xem ${room.code}`}>
                  <Eye className="size-4" />
                </Link>
                <Link href={`/rooms/${room.id}/edit`} title={`Sửa ${room.code}`}>
                  <Pencil className="size-4" />
                </Link>
              </div>
            ),
          },
        ]}
        items={rooms.items}
      />
    </div>
  );
}
