import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  IonApp, IonBadge, IonContent, IonHeader, IonItem, IonLabel, IonList, IonNote,
  IonSegment, IonSegmentButton, IonTitle, IonToolbar,
} from '@ionic/angular/standalone';

import { apiUrl } from './api';
import { WorkItem } from './work-item';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, IonApp, IonBadge, IonContent, IonHeader, IonItem, IonLabel, IonList,
    IonNote, IonSegment, IonSegmentButton, IonTitle, IonToolbar,
  ],
  template: `
    <ion-app>
      <ion-header>
        <ion-toolbar><ion-title>{{ title }}</ion-title></ion-toolbar>
        <ion-toolbar>
          <ion-segment [value]="screen()" (ionChange)="screen.set($any($event).detail.value)">
            <ion-segment-button *ngFor="let name of screens" [value]="name">
              <ion-label>{{ name }}</ion-label>
            </ion-segment-button>
          </ion-segment>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <ion-note color="danger" *ngIf="error()">{{ error() }}</ion-note>
        <ion-list *ngIf="screen() === screens[0]; else detail">
          <ion-item *ngFor="let item of items()" button (click)="select(item)">
            <ion-label>
              <h2>{{ item.title }}</h2>
              <p>{{ item.location }}</p>
            </ion-label>
            <ion-badge slot="end" [color]="colour(item.status)">{{ item.status }}</ion-badge>
          </ion-item>
        </ion-list>
        <ng-template #detail>
          <div *ngIf="selected() as item; else empty">
            <h2>{{ item.title }}</h2>
            <p>Location: {{ item.location }}</p>
            <p>Priority: {{ item.priority }}</p>
            <p>Status: {{ item.status }}</p>
          </div>
          <ng-template #empty><p>Select a work item from the queue.</p></ng-template>
        </ng-template>
      </ion-content>
    </ion-app>
  `,
})
export class AppComponent {
  readonly title = 'Field Service Work Orders';
  readonly screens = ["Work Order Queue mockup with specification panel]", "Asset Detail and Diagnostics mockup with specification panel", "Service Log and Parts mockup with specification panel]", "Completion and Sign-off mockup with specification panel]"];
  readonly screen = signal("Work Order Queue mockup with specification panel]");
  readonly items = signal<WorkItem[]>([]);
  readonly selected = signal<WorkItem | null>(null);
  readonly error = signal('');
  private readonly http = inject(HttpClient);

  constructor() {
    this.http.get<WorkItem[]>(apiUrl('/api/work-items')).subscribe({
      next: (items) => this.items.set(items),
      error: () => this.error.set('Could not reach the API.'),
    });
  }

  select(item: WorkItem): void {
    this.selected.set(item);
    this.screen.set(this.screens[1] ?? this.screens[0]);
  }

  colour(status: string): string {
    return status === 'complete' ? 'success' : status === 'in-progress' ? 'warning' : 'medium';
  }
}
