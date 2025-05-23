// src/componentes/ui/InputTexto.jsx (sugerido, se className for para o input)
export default function InputTexto({ label, name, value, onChange, type = "text", className = "" }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-1">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        className={`w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-green-500 ${className}`} // className aplicado ao input
      />
    </div>
  );
}