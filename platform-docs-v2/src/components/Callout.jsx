/**
 * Callout component for Markdoc-rendered callouts.
 * Types: tip, note, warning, success, important
 */
export default function Callout({ type = 'note', title, children }) {
  const icons = {
    tip: '💡',
    note: 'ℹ️',
    warning: '⚠️',
    success: '✅',
    important: '🔑',
  };
  const borderColors = {
    tip: 'border-emerald-500',
    note: 'border-blue-500',
    warning: 'border-amber-500',
    success: 'border-green-500',
    important: 'border-purple-500',
  };
  const bgColors = {
    tip: 'bg-emerald-50 dark:bg-emerald-900/20',
    note: 'bg-blue-50 dark:bg-blue-900/20',
    warning: 'bg-amber-50 dark:bg-amber-900/20',
    success: 'bg-green-50 dark:bg-green-900/20',
    important: 'bg-purple-50 dark:bg-purple-900/20',
  };

  return (
    <div className={`callout rounded-xl border-l-4 ${borderColors[type] || borderColors.note} ${bgColors[type] || bgColors.note} p-4 my-6`}>
      <div className="flex items-start gap-2">
        <span className="text-lg mt-0.5">{icons[type] || icons.note}</span>
        <div className="flex-1 prose-custom prose-sm">
          {title && <strong className="block mb-1">{title}</strong>}
          {children}
        </div>
      </div>
    </div>
  );
}
