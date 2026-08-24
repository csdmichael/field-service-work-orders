export interface WorkItem {
  id: number;
  title: string;
  status: 'new' | 'in-progress' | 'complete';
  priority: 'low' | 'normal' | 'high';
  location: string;
}
