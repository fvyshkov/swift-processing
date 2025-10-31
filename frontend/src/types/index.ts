export interface ProcessType {
  id: string;
  code: string;
  name_en: string;
  name_ru: string;
  attributes_table?: string;
  parent_id?: string;
}

export interface ProcessState {
  id: string;
  type_id: string;
  code: string;
  name_en: string;
  name_ru: string;
  color_code?: string;
  allow_edit: boolean;
  allow_delete: boolean;
  start: boolean;
  operation_list_script?: string;
}

export interface ProcessOperation {
  id: string;
  type_id: string;
  code: string;
  name_en: string;
  name_ru: string;
  icon?: string;
  resource_url?: string;
  availability_condition?: string;
  cancel: boolean;
  move_to_state_script?: string;
  workflow?: string;
  database?: string;
  available_state_ids?: string[];
}

export interface SaveAllRequest {
  type?: ProcessType;
  states?: {
    created: ProcessState[];
    updated: ProcessState[];
    deleted: string[];
  };
  operations?: {
    created: ProcessOperation[];
    updated: ProcessOperation[];
    deleted: string[];
  };
  operation_states?: {
    [operation_id: string]: string[];
  };
}

