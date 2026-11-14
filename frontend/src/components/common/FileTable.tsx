import React from 'react';
import { ArrowDown, ArrowUp, ArrowUpDown, ExternalLink, FileWarning } from 'lucide-react';
import { FileRecord } from '../../types';
import { formatBytes, formatNumber } from '../../utils/format';
import { Badge, downloadStatusLabel, downloadStatusTone } from './Badge';

export type FileSortField = 'filename' | 'size' | 'extension' | 'dataset' | 'investigation';

interface FileTableProps {
  files: FileRecord[];
  showInvestigation?: boolean;
  sortBy?: FileSortField;
  order?: 'asc' | 'desc';
  onSort?: (field: FileSortField) => void;
}

const SortHeader: React.FC<{
  field: FileSortField;
  label: string;
  sortBy?: FileSortField;
  order?: 'asc' | 'desc';
  onSort?: (field: FileSortField) => void;
  align?: 'left' | 'right';
}> = ({ field, label, sortBy, order, onSort, align = 'left' }) => {
  const active = sortBy === field;
  const Icon = active ? (order === 'asc' ? ArrowUp : ArrowDown) : ArrowUpDown;
  return (
    <th
      scope="col"
      className={`whitespace-nowrap px-3 py-2.5 text-[10px] font-mono uppercase tracking-wider text-[#64748B] ${
        align === 'right' ? 'text-right' : 'text-left'
      }`}
    >
      {onSort ? (
        <button
          onClick={() => onSort(field)}
          className={`inline-flex items-center gap-1 transition-colors hover:text-[#35C6E8] ${
            active ? 'text-[#35C6E8]' : ''
          }`}
        >
          {label}
          <Icon className="h-3 w-3" />
        </button>
      ) : (
        label
      )}
    </th>
  );
};

export const FileTable: React.FC<FileTableProps> = ({
  files,
  showInvestigation = false,
  sortBy,
  order,
  onSort,
}) => {
  if (files.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-[#243449] px-4 py-10 text-center text-sm text-[#64748B]">
        No files match the current filters.
      </div>
    );
  }

  return (
    <div className="-mx-1 overflow-x-auto">
      <table className="min-w-full border-collapse text-left">
        <thead className="border-b border-[#243449]">
          <tr>
            <SortHeader
              field="filename"
              label="Filename"
              sortBy={sortBy}
              order={order}
              onSort={onSort}
            />
            {showInvestigation && (
              <SortHeader
                field="investigation"
                label="Investigation"
                sortBy={sortBy}
                order={order}
                onSort={onSort}
              />
            )}
            <SortHeader
              field="extension"
              label="Format"
              sortBy={sortBy}
              order={order}
              onSort={onSort}
            />
            <SortHeader
              field="size"
              label="Remote size"
              sortBy={sortBy}
              order={order}
              onSort={onSort}
              align="right"
            />
            <th
              scope="col"
              className="px-3 py-2.5 text-left text-[10px] font-mono uppercase tracking-wider text-[#64748B]"
            >
              Download status
            </th>
            <SortHeader
              field="dataset"
              label="Dataset group"
              sortBy={sortBy}
              order={order}
              onSort={onSort}
            />
            <th
              scope="col"
              className="px-3 py-2.5 text-left text-[10px] font-mono uppercase tracking-wider text-[#64748B]"
            >
              Source
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#243449]/60">
          {files.map((file) => (
            <tr key={file.file_id} className="align-top transition-colors hover:bg-[#0C1626]/40">
              <td className="max-w-[22rem] px-3 py-2.5">
                <p className="break-all font-mono text-xs text-[#F4F7FB]" title={file.filename}>
                  {file.filename}
                </p>
                <div className="mt-1 flex flex-wrap items-center gap-1.5">
                  {file.empty_file && (
                    <Badge tone="amber" title="The file exists in the inventory but reported 0 bytes.">
                      <FileWarning className="h-3 w-3" /> Zero-byte
                    </Badge>
                  )}
                  {file.restricted && <Badge tone="red">Restricted</Badge>}
                  {!file.visible && <Badge tone="slate">Hidden</Badge>}
                  <span className="font-mono text-[10px] text-[#64748B]">
                    {file.mime_type ?? file.format_category ?? 'unknown type'}
                  </span>
                </div>
              </td>
              {showInvestigation && (
                <td className="whitespace-nowrap px-3 py-2.5">
                  <span className="rounded border border-[#243449] bg-[#0C1626] px-2 py-0.5 font-mono text-[11px] text-[#35C6E8]">
                    {file.investigation_id}
                  </span>
                </td>
              )}
              <td className="whitespace-nowrap px-3 py-2.5 font-mono text-xs text-[#94A3B8]">
                {file.extension ?? '—'}
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 text-right font-mono text-xs text-[#F4F7FB]">
                {file.size_known ? formatBytes(file.size_bytes) : 'Unknown'}
                {file.size_known && (
                  <p className="text-[10px] text-[#64748B]">
                    {formatNumber(file.size_bytes ?? 0)} B remote
                  </p>
                )}
              </td>
              <td className="px-3 py-2.5">
                <Badge tone={downloadStatusTone(file.download_status)}>
                  {downloadStatusLabel(file.download_status)}
                </Badge>
                <p className="mt-1 font-mono text-[10px] text-[#64748B]">
                  Local: {file.downloaded ? formatBytes(file.local_size_bytes) : '0 B'}
                </p>
              </td>
              <td
                className="max-w-[12rem] truncate px-3 py-2.5 font-mono text-xs text-[#94A3B8]"
                title={file.dataset_name ?? undefined}
              >
                {file.dataset_name ?? '—'}
              </td>
              <td className="whitespace-nowrap px-3 py-2.5">
                {file.download_url ? (
                  <a
                    href={file.download_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Opens the NASA PSI download endpoint. It returns a signed S3 redirect; no file has been downloaded by FlameLens."
                    className="inline-flex items-center gap-1 text-xs font-medium text-[#35C6E8] hover:text-[#F4F7FB]"
                  >
                    PSI source
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ) : (
                  <span className="text-xs text-[#64748B]">—</span>
                )}
                {file.legacy_url_status && (
                  <p className="mt-1 font-mono text-[10px] text-[#64748B]">
                    Legacy: {file.legacy_url_status}
                  </p>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
