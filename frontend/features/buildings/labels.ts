export function houseTypeLabel(value: string) {
  const labels: Record<string, string> = {
    boarding_house: "Nhà trọ",
    mini_apartment: "Chung cư mini",
    dormitory: "Ký túc xá",
    whole_house: "Nhà nguyên căn",
  };
  return labels[value] ?? value;
}

export function buildingStatusLabel(value: string) {
  const labels: Record<string, string> = {
    active: "Đang hoạt động",
    temporarily_closed: "Tạm đóng",
    under_renovation: "Đang sửa chữa",
  };
  return labels[value] ?? value;
}

export function amenityLabel(value: string) {
  const labels: Record<string, string> = {
    wifi: "Wifi",
    camera: "Camera",
    elevator: "Thang máy",
    shared_washing_machine: "Máy giặt chung",
    parking: "Bãi xe",
    security: "Bảo vệ",
  };
  return labels[value] ?? value;
}
