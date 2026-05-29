export const roomTypes = [
  ["standard", "Phòng tiêu chuẩn"],
  ["studio", "Studio"],
  ["loft", "Gác lửng"],
  ["shared_room", "Phòng ghép"],
  ["dorm_bed", "Giường ký túc"],
] as const;

export const roomStatuses = [
  ["vacant", "Trống"],
  ["occupied", "Đang thuê"],
  ["reserved", "Đã giữ chỗ"],
  ["maintenance", "Bảo trì"],
  ["unavailable", "Ngưng sử dụng"],
] as const;

export function roomTypeLabel(value: string) {
  return roomTypes.find(([key]) => key === value)?.[1] ?? value;
}

export function roomStatusLabel(value: string) {
  return roomStatuses.find(([key]) => key === value)?.[1] ?? value;
}

export function roomStatusTone(value: string): "green" | "amber" | "red" | "slate" {
  if (value === "occupied") return "green";
  if (value === "vacant") return "slate";
  if (value === "maintenance" || value === "unavailable") return "red";
  return "amber";
}
