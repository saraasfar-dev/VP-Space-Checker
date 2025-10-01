import React from "react";

const SeoChecker = ({ data }) => {
  // Helper function to check title length
  const isTitleInvalid = (title) => {
    if (!title) return false;
    return title.length > 80; // titles exceeding 80 chars = invalid
  };

  // Helper function to check description length
  const isDescriptionInvalid = (description) => {
    if (!description) return false;
    return description.length < 130 || description.length > 180; // valid range is 130–180
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">SEO Meta Checker</h2>
      <table className="table-auto w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-200">
            <th className="border border-gray-300 px-4 py-2">Page</th>
            <th className="border border-gray-300 px-4 py-2">Meta Title</th>
            <th className="border border-gray-300 px-4 py-2">Meta Description</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => {
            const titleInvalid = isTitleInvalid(item.title);
            const descInvalid = isDescriptionInvalid(item.description);

            return (
              <tr key={index}>
                <td className="border border-gray-300 px-4 py-2">{item.page}</td>
                <td
                  className={`border border-gray-300 px-4 py-2 ${
                    titleInvalid ? "text-red-600 font-semibold" : ""
                  }`}
                >
                  {item.title || "N/A"}{" "}
                  {titleInvalid && (
                    <span className="ml-2 text-xs text-red-500">
                      ({item.title.length} chars)
                    </span>
                  )}
                </td>
                <td
                  className={`border border-gray-300 px-4 py-2 ${
                    descInvalid ? "text-red-600 font-semibold" : ""
                  }`}
                >
                  {item.description || "N/A"}{" "}
                  {descInvalid && (
                    <span className="ml-2 text-xs text-red-500">
                      ({item.description.length} chars)
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default SeoChecker;
