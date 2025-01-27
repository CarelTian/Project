#ifndef GDWG_GRAPH_H
#define GDWG_GRAPH_H

#include <initializer_list>
#include <algorithm>
#include <compare>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <sstream>
#include <vector>
// TODO: Make both graph and edge generic
//       ... this won't just compile
//       straight away
namespace gdwg {

	template<typename N, typename E>
	class graph;

	template<typename N, typename E>
	class edge {
	 public:
		edge(N s, N d)
		: src(s)
		, dst(d) {}
		virtual ~edge() = default;
		virtual auto print_edge() const -> std::string = 0;
		virtual auto is_weighted() const -> bool = 0;
		virtual auto get_weight() const -> std::optional<E> = 0;
		virtual auto get_nodes() const -> std::pair<N, N> = 0;
		virtual auto operator==(edge<N, E> const& other) const -> bool = 0;

		// Please forgive me best practices. I know the definition should not be written in the in the class with
		// declarations
		//  But C++20 is too difficult. I tried to separate it but encountered errors that I can't solve.
		friend auto operator<=>(edge<N, E> const& lhs, edge<N, E> const& rhs) -> std::strong_ordering {
			if (lhs.src < rhs.src)
				return std::strong_ordering::less;
			if (lhs.src > rhs.src)
				return std::strong_ordering::greater;
			if (lhs.dst < rhs.dst)
				return std::strong_ordering::less;
			if (lhs.dst > rhs.dst)
				return std::strong_ordering::greater;
			if (!lhs.is_weighted() && rhs.is_weighted())
				return std::strong_ordering::less;
			if (lhs.is_weighted() && !rhs.is_weighted())
				return std::strong_ordering::greater;
			if (lhs.is_weighted() && rhs.is_weighted()) {
				if (lhs.get_weight() < rhs.get_weight())
					return std::strong_ordering::less;
				if (lhs.get_weight() > rhs.get_weight())
					return std::strong_ordering::greater;
			}
			return std::strong_ordering::equal;
		}
		N src;
		N dst;
		E weight;

	 private:
		// You may need to add data members and member functions
		friend class graph<N, E>;
	};

	template<typename N, typename E>
	class weighted_edge : public edge<N, E> {
	 public:
		weighted_edge(N s, N d, E w)
		: edge<N, E>(s, d)
		, weight(w) {}
		auto print_edge() const -> std::string override;
		auto is_weighted() const -> bool override;
		auto get_weight() const -> std::optional<E> override;
		auto get_nodes() const -> std::pair<N, N> override;
		auto operator==(edge<N, E> const& other) const -> bool override;

	 private:
		E weight;
	};

	template<typename N, typename E>
	class unweighted_edge : public edge<N, E> {
	 public:
		unweighted_edge(N s, N d)
		: edge<N, E>(s, d){};
		auto print_edge() const -> std::string override;
		auto is_weighted() const -> bool override;
		auto get_weight() const -> std::optional<E> override;
		auto get_nodes() const -> std::pair<N, N> override;
		auto operator==(edge<N, E> const& other) const -> bool override;

	 private:
		E weight;
	};

	template<typename N, typename E>
	class graph {
	 public:
		using edge = gdwg::edge<N, E>;
		using weighted_edge = gdwg::weighted_edge<N, E>;
		using unweighted_edge = gdwg::unweighted_edge<N, E>;

		class iterator {
		 public:
			using value_type = struct {
				N from;
				N to;
				std::optional<E> weight;
			};
			using reference = value_type;
			using pointer = void;
			using difference_type = std::ptrdiff_t;
			using iterator_category = std::bidirectional_iterator_tag;

			// Iterator constructor
			iterator() = default;
			auto operator*() const -> reference;
			auto operator++() -> iterator&;
			auto operator++(int) -> iterator;
			auto operator--() -> iterator&;
			auto operator--(int) -> iterator;
			auto operator==(iterator const& other) const -> bool;

		 private:
			friend class graph<N, E>;
			iterator(typename std::vector<std::shared_ptr<edge>>::const_iterator it)
			: current_edge_it(it) {}
			typename std::vector<std::shared_ptr<edge>>::const_iterator current_edge_it;
		};

		// Your member functions go here
		graph() = default;
		graph(std::initializer_list<N> il);
		graph(graph&& other) noexcept;
		graph(graph const& other);
		template<typename InputIt>
		graph(InputIt first, InputIt last) {
			for (auto it = first; it != last; ++it) {
				insert_node(*it);
			}
		}
		auto operator=(graph&& other) -> graph&;
		auto operator=(graph const& other) -> graph&;
		auto insert_node(N const& value) -> bool;
		auto insert_edge(N const& src, N const& dst, std::optional<E> weight = std::nullopt) -> bool;
		auto replace_node(N const& old_data, N const& new_data) -> bool;
		auto merge_replace_node(N const& old_data, N const& new_data) -> void;
		auto erase_node(N const& value) -> bool;
		auto erase_edge(N const& src, N const& dst, std::optional<E> weight = std::nullopt) -> bool;
		auto erase_edge(iterator i) -> iterator;
		auto erase_edge(iterator i, iterator s) -> iterator;
		auto clear() noexcept -> void;
		[[nodiscard]] auto is_node(N const& value) const -> bool;
		[[nodiscard]] auto is_connected(N const& src, N const& dst) -> bool;
		[[nodiscard]] auto empty() const -> bool;
		[[nodiscard]] auto nodes() const -> std::vector<N>;
		[[nodiscard]] auto edges(N const& src, N const& dst) const -> std::vector<std::unique_ptr<edge>>;
		[[nodiscard]] auto find(N const& src, N const& dst, std::optional<E> weight = std::nullopt) -> iterator;
		[[nodiscard]] auto connections(N const& src) const -> std::vector<N>;
		[[nodiscard]] auto operator==(graph const& other) const -> bool;
		[[nodiscard]] auto begin() const -> iterator;
		[[nodiscard]] auto end() const -> iterator;
		friend auto operator<< <>(std::ostream& os, graph const& g) -> std::ostream&;

	 private:
		std::set<N> nodess;
		std::map<N, std::vector<std::shared_ptr<edge>>> edgess;
		std::vector<std::shared_ptr<edge>> ordered_edges;
		auto sort() -> void;
	};

	template<typename N, typename E>
	auto graph<N, E>::sort() -> void {
		std::sort(ordered_edges.begin(),
		          ordered_edges.end(),
		          [](const std::shared_ptr<edge>& lhs, const std::shared_ptr<edge>& rhs) {
			          if (lhs->src < rhs->src)
				          return true;
			          else if (lhs->src > rhs->src)
				          return false;
			          if (lhs->dst < rhs->dst)
				          return true;
			          else if (lhs->dst > rhs->dst)
				          return false;
			          if (not lhs->is_weighted() and rhs->is_weighted())
				          return true;
			          else if (lhs->is_weighted() and not rhs->is_weighted())
				          return false;
			          if (lhs->is_weighted() and rhs->is_weighted()) {
				          return *lhs->get_weight() < *rhs->get_weight();
			          }
			          return false;
		          });
	}
	template<typename N, typename E>
	graph<N, E>::graph(std::initializer_list<N> il) {
		for (const auto& node : il) {
			nodess.insert(node);
		}
	}
	template<typename N, typename E>
	graph<N, E>::graph(graph&& other) noexcept
	: nodess(std::move(other.nodess))
	, edgess(std::move(other.edgess))
	, ordered_edges(std::move(other.ordered_edges)) {
		other.nodess.clear();
		other.edgess.clear();
		other.ordered_edges.clear();
	}
	template<typename N, typename E>
	graph<N, E>::graph(graph const& other)
	: nodess(other.nodess)
	, edgess(other.edgess)
	, ordered_edges(other.ordered_edges) {}
	template<typename N, typename E>
	auto graph<N, E>::operator=(graph&& other) -> graph& {
		if (this != &other) {
			nodess.clear();
			edgess.clear();
			nodess = std::move(other.nodess);
			edgess = std::move(other.edgess);
			ordered_edges = std::move(other.ordered_edges);
			other.nodess.clear();
			other.edgess.clear();
			other.ordered_edges.clear();
		}
		return *this;
	}
	template<typename N, typename E>
	auto graph<N, E>::operator=(graph const& other) -> graph& {
		if (this != &other) {
			graph<N, E> temp(other);
			std::swap(nodess, temp.nodess);
			std::swap(edgess, temp.edgess);
			std::swap(ordered_edges, temp.ordered_edges);
		}
		return *this;
	}

	template<typename N, typename E>
	auto weighted_edge<N, E>::get_nodes() const -> std::pair<N, N> {
		return {this->src, this->dst};
	}

	template<typename N, typename E>
	auto weighted_edge<N, E>::print_edge() const -> std::string {
		std::ostringstream oss;
		oss << this->src << " -> " << this->dst << " | W | " << this->weight;
		return oss.str();
	}

	template<typename N, typename E>
	auto weighted_edge<N, E>::is_weighted() const -> bool {
		return true;
	}

	template<typename N, typename E>
	auto weighted_edge<N, E>::get_weight() const -> std::optional<E> {
		return weight;
	}
	template<typename N, typename E>
	auto weighted_edge<N, E>::operator==(edge<N, E> const& other) const -> bool {
		if (auto* o = dynamic_cast<const weighted_edge*>(&other)) {
			return this->src == o->src && this->dst == o->dst && this->weight == o->weight;
		}
		return false;
	}

	template<typename N, typename E>
	auto unweighted_edge<N, E>::get_nodes() const -> std::pair<N, N> {
		return {this->src, this->dst};
	}

	template<typename N, typename E>
	auto unweighted_edge<N, E>::print_edge() const -> std::string {
		std::ostringstream oss;
		oss << this->src << " -> " << this->dst << " | U";
		return oss.str();
	}

	template<typename N, typename E>
	auto unweighted_edge<N, E>::is_weighted() const -> bool {
		return false;
	}

	template<typename N, typename E>
	auto unweighted_edge<N, E>::get_weight() const -> std::optional<E> {
		return {};
	}
	template<typename N, typename E>
	auto unweighted_edge<N, E>::operator==(edge<N, E> const& other) const -> bool {
		if (auto* o = dynamic_cast<const unweighted_edge*>(&other)) {
			return this->src == o->src && this->dst == o->dst;
		}
		return false;
	}
	template<typename N, typename E>
	auto graph<N, E>::insert_node(N const& value) -> bool {
		return nodess.insert(value).second;
	}
	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::is_node(N const& value) const -> bool {
		return nodess.find(value) != nodess.end();
	}
	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::empty() const -> bool {
		return nodess.empty();
	}
	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::operator==(graph const& other) const -> bool {
		if (nodess != other.nodess) {
			return false;
		}

		if (edgess.size() != other.edgess.size()) {
			return false;
		}

		for (const auto& [node, edge_list] : edgess) {
			if (other.edgess.find(node) == other.edgess.end()) {
				return false;
			}

			const auto& other_edge_list = other.edgess.at(node);
			if (edge_list.size() != other_edge_list.size()) {
				return false;
			}

			for (size_t i = 0; i < edge_list.size(); ++i) {
				if (*(edge_list[i]) != *(other_edge_list[i])) {
					return false;
				}
			}
		}
		return true;
	}

	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::is_connected(N const& src, N const& dst) -> bool {
		if (not is_node(src) or not is_node(dst)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::is_connected if src or dst node don't exist in "
			                         "the graph");
		}

		const auto& edge_list = edgess.find(src);
		if (edge_list != edgess.end()) {
			for (const auto& edge : edge_list->second) {
				if (edge->dst == dst) {
					return true;
				}
			}
		}
		const auto& edge_list_reverse = edgess.find(dst);
		if (edge_list_reverse != edgess.end()) {
			for (const auto& edge : edge_list_reverse->second) {
				if (edge->dst == src) {
					return true;
				}
			}
		}
		return false;
	}
	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::nodes() const -> std::vector<N> {
		std::vector<N> node_list(nodess.begin(), nodess.end());
		std::sort(node_list.begin(), node_list.end());
		return node_list;
	}

	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::edges(N const& src, N const& dst) const -> std::vector<std::unique_ptr<edge>> {
		if (not is_node(src) or not is_node(dst)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::edges if src or dst node don't exist in the "
			                         "graph");
		}
		std::vector<std::unique_ptr<edge>> edge_result;
		auto it = edgess.find(src);
		if (it != edgess.end()) {
			for (const auto& e : it->second) {
				if (e->dst == dst) {
					if (e->is_weighted()) {
						edge_result.push_back(std::make_unique<weighted_edge>(e->src, e->dst, *e->get_weight()));
					}
					else {
						edge_result.push_back(std::make_unique<unweighted_edge>(e->src, e->dst));
					}
				}
			}
		}
		std::sort(edge_result.begin(),
		          edge_result.end(),
		          [](const std::unique_ptr<edge>& lhs, const std::unique_ptr<edge>& rhs) {
			          if (not lhs->is_weighted() and rhs->is_weighted()) {
				          return true; // unweighted edge comes first
			          }
			          else if (lhs->is_weighted() and not rhs->is_weighted()) {
				          return false; // weighted edge comes after unweighted edge
			          }
			          else if (lhs->is_weighted() and rhs->is_weighted()) {
				          return *lhs->get_weight() < *rhs->get_weight(); // sort by weight
			          }
			          return false;
		          });

		return edge_result;
	}
	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::find(N const& src, N const& dst, std::optional<E> weight) -> iterator {
		if (not nodess.contains(src)) {
			return end();
		}
		auto& edge_list = edgess[src];
		// Lambda function to check if an edge matches the criteria
		auto edge_match = [&src, &dst, &weight](const std::shared_ptr<edge>& e) {
			if (e->src == src && e->dst == dst) {
				if (weight.has_value()) {
					return e->is_weighted() and e->get_weight() == weight;
				}
				else {
					return not e->is_weighted();
				}
			}
			return false;
		};
		// Find the edge in the edge_list
		auto it = std::find_if(ordered_edges.begin(), ordered_edges.end(), edge_match);
		if (it != edge_list.end()) {
			return iterator(it);
		}
		return end();
	}

	template<typename N, typename E>
	[[nodiscard]] auto graph<N, E>::connections(N const& src) const -> std::vector<N> {
		if (not is_node(src)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::connections if src doesn't exist in the graph");
		}

		std::set<N> connected_nodes;
		auto it = edgess.find(src);
		if (it != edgess.end()) {
			for (const auto& e : it->second) {
				connected_nodes.insert(e->dst);
			}
		}

		std::vector<N> result(connected_nodes.begin(), connected_nodes.end());
		std::sort(result.begin(), result.end());
		return result;
	}
	template<typename N, typename E>
	auto graph<N, E>::begin() const -> iterator {
		return iterator(ordered_edges.begin());
	}

	template<typename N, typename E>
	auto graph<N, E>::end() const -> iterator {
		return iterator(ordered_edges.end());
	}

	template<typename N, typename E>
	auto graph<N, E>::insert_edge(N const& src, N const& dst, std::optional<E> weight) -> bool {
		if (not nodess.contains(src) or not nodess.contains(dst)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::insert_edge when either src or dst node does not "
			                         "exist");
		}
		std::shared_ptr<edge> new_edge;
		if (weight) {
			new_edge = std::make_shared<weighted_edge>(src, dst, *weight);
		}
		else {
			new_edge = std::make_shared<unweighted_edge>(src, dst);
		}

		auto& edge_list = edgess[src];
		if (std::find_if(edge_list.begin(),
		                 edge_list.end(),
		                 [&new_edge](const std::shared_ptr<edge>& e) { return *e == *new_edge; })
		    != edge_list.end())
		{
			return false;
		}
		edge_list.push_back(new_edge);
		// update ordered_edges
		auto pos = std::upper_bound(
		    ordered_edges.begin(),
		    ordered_edges.end(),
		    new_edge,
		    [](const std::shared_ptr<edge>& lhs, const std::shared_ptr<edge>& rhs) { return *lhs < *rhs; });
		ordered_edges.insert(pos, new_edge);

		return true;
	}

	template<typename N, typename E>
	auto graph<N, E>::replace_node(N const& old_data, N const& new_data) -> bool {
		if (not nodess.contains(old_data)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::replace_node on a node that doesn't exist");
		}
		if (nodess.contains(new_data)) {
			return false;
		}
		nodess.erase(old_data);
		nodess.insert(new_data);
		std::vector<std::shared_ptr<edge>> temp_edges;
		if (edgess.contains(old_data)) {
			edgess[new_data] = std::move(edgess[old_data]);
			edgess.erase(old_data);
			for (auto& edge : edgess[new_data]) {
				edge->src = new_data;
				temp_edges.push_back(edge);
			}
		}

		for (auto& [src, edge_list] : edgess) {
			for (auto& edge : edge_list) {
				if (edge->dst == old_data) {
					edge->dst = new_data;
					temp_edges.push_back(edge);
				}
			}
		}
		ordered_edges.erase(std::remove_if(ordered_edges.begin(),
		                                   ordered_edges.end(),
		                                   [&old_data](const std::shared_ptr<edge>& edge) {
			                                   return edge->src == old_data || edge->dst == old_data;
		                                   }),
		                    ordered_edges.end());
		ordered_edges.insert(ordered_edges.end(), temp_edges.begin(), temp_edges.end());
		sort();

		return true;
	}
	template<typename N, typename E>
	auto graph<N, E>::merge_replace_node(N const& old_data, N const& new_data) -> void {
		if (not nodess.contains(old_data) or not nodess.contains(new_data)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::merge_replace_node on old or new data if they "
			                         "don't exist in the graph");
		}
		// Handle outgoing edgess from old_data
		if (edgess.contains(old_data)) {
			for (const auto& it : edgess[old_data]) {
				std::shared_ptr<edge> new_edge;
				if (it->is_weighted()) {
					new_edge = std::make_shared<weighted_edge>(new_data, it->dst, *it->get_weight());
				}
				else {
					new_edge = std::make_shared<unweighted_edge>(new_data, it->dst);
				}

				if (std::find_if(edgess[new_data].begin(),
				                 edgess[new_data].end(),
				                 [&new_edge](const std::shared_ptr<edge>& e) { return *e == *new_edge; })
				    == edgess[new_data].end())
				{
					edgess[new_data].push_back(new_edge);
					ordered_edges.push_back(new_edge);
				}
			}
			edgess.erase(old_data);
			ordered_edges.erase(std::remove_if(ordered_edges.begin(),
			                                   ordered_edges.end(),
			                                   [&old_data](const std::shared_ptr<edge>& edge) {
				                                   return edge->src == old_data or edge->dst == old_data;
			                                   }),
			                    ordered_edges.end());
		}
		// Handle incoming edgess to old_data
		std::vector<std::shared_ptr<edge>> op_list;
		for (auto& [src, edge_list] : edgess) {
			for (const auto& it : edge_list) {
				if (it->dst == old_data) {
					op_list.push_back(it);
				}
			}
		}
		for (const auto& it : op_list) {
			insert_edge(it->src, new_data, it->get_weight());
			auto& edge_list = edgess[it->src];
			edge_list.erase(std::remove(edge_list.begin(), edge_list.end(), it), edge_list.end());
		}
		nodess.erase(old_data);
		sort();
	}
	template<typename N, typename E>
	auto graph<N, E>::erase_node(N const& value) -> bool {
		if (not is_node(value)) {
			return false;
		}
		for (auto& [src, edge_list] : edgess) {
			edge_list.erase(std::remove_if(edge_list.begin(),
			                               edge_list.end(),
			                               [&value](const std::shared_ptr<edge>& e) { return e->dst == value; }),
			                edge_list.end());
		}
		edgess.erase(value);
		nodess.erase(value);
		ordered_edges.erase(std::remove_if(ordered_edges.begin(),
		                                   ordered_edges.end(),
		                                   [&value](const std::shared_ptr<edge>& edge) {
			                                   return edge->src == value or edge->dst == value;
		                                   }),
		                    ordered_edges.end());
		return true;
	}
	template<typename N, typename E>
	auto graph<N, E>::erase_edge(N const& src, N const& dst, std::optional<E> weight) -> bool {
		if (not is_node(src) or not is_node(dst)) {
			throw std::runtime_error("Cannot call gdwg::graph<N, E>::erase_edge on src or dst if they don't exist in "
			                         "the graph");
		}

		auto it = edgess.find(src);
		if (it == edgess.end()) {
			return false;
		}

		auto& edge_list = it->second;
		auto edge_it = std::remove_if(edge_list.begin(), edge_list.end(), [&dst, &weight](const std::shared_ptr<edge>& e) {
			if (e->dst != dst) {
				return false;
			}
			if (weight) {
				return e->is_weighted() and *e->get_weight() == *weight;
			}
			else {
				return not e->is_weighted();
			}
		});
		if (edge_it == edge_list.end()) {
			return false;
		}
		auto ordered_edge_it = std::remove_if(ordered_edges.begin(),
		                                      ordered_edges.end(),
		                                      [&src, &dst, &weight](const std::shared_ptr<edge>& e) {
			                                      if (weight)
				                                      return e->src == src and e->dst == dst
				                                             and *e->get_weight() == weight;
			                                      else
				                                      return e->src == src and e->dst == dst and not e->is_weighted();
		                                      });
		edge_list.erase(edge_it, edge_list.end());
		ordered_edges.erase(ordered_edge_it, ordered_edges.end());
		return true;
	}
	template<typename N, typename E>
	auto graph<N, E>::erase_edge(iterator i) -> iterator {
		if (i == end())
			return i;
		auto edge_it = i.current_edge_it;
		auto next_it = std::next(edge_it);

		auto& edges = edgess[(*edge_it)->src];
		edges.erase(
		    std::remove_if(edges.begin(), edges.end(), [&](const std::shared_ptr<edge>& e) { return e == *edge_it; }),
		    edges.end());

		ordered_edges.erase(edge_it);

		return iterator(next_it);
	}
	template<typename N, typename E>
	auto graph<N, E>::erase_edge(iterator i, iterator s) -> iterator {
		auto edge_it = i.current_edge_it;
		auto end_it = s.current_edge_it;
		auto list = std::vector<std::shared_ptr<edge>>{};
		while (edge_it != end_it) {
			auto& edges = edgess[(*edge_it)->src];
			edges.erase(
			    std::remove_if(edges.begin(), edges.end(), [&](const std::shared_ptr<edge>& e) { return e == *edge_it; }),
			    edges.end());
			list.push_back(*edge_it);
			edge_it++;
		}
		for (const auto& edge : list) {
			ordered_edges.erase(std::remove(ordered_edges.begin(), ordered_edges.end(), edge), ordered_edges.end());
		}
		return s;
	}
	template<typename N, typename E>
	auto graph<N, E>::clear() noexcept -> void {
		auto list = nodes();
		for (const auto& n : list) {
			erase_node(n);
		}
	}
	template<typename N, typename E>
	auto operator<<(std::ostream& os, graph<N, E> const& g) -> std::ostream& {
		auto it = g.begin();
		auto end = g.end();
		os << std::endl;
		for (const auto& node : g.nodess) {
			os << node << " (" << std::endl;
			while (it != end) {
				if ((*it).from != node)
					break;
				os << "  " << node << " -> " << (*it).to << " | ";
				if ((*it).weight)
					os << "W | " << *(*it).weight;
				else
					os << "U";
				os << std::endl;
				++it;
			}
			os << ")" << std::endl;
		}
		return os;
	}

	template<typename N, typename E>
	auto graph<N, E>::iterator::operator*() const -> reference {
		const auto& e = *current_edge_it;
		return reference{e->src, e->dst, e->get_weight()};
	}
	template<typename N, typename E>
	auto graph<N, E>::iterator::operator++() -> iterator& {
		++current_edge_it;
		return *this;
	}
	template<typename N, typename E>
	auto graph<N, E>::iterator::operator++(int) -> iterator {
		auto temp = *this;
		++(*this);
		return temp;
	}

	template<typename N, typename E>
	auto graph<N, E>::iterator::operator--() -> iterator& {
		--current_edge_it;
		return *this;
	}
	template<typename N, typename E>
	auto graph<N, E>::iterator::operator--(int) -> iterator {
		auto temp = *this;
		--(*this);
		return temp;
	}
	template<typename N, typename E>
	auto graph<N, E>::iterator::operator==(iterator const& other) const -> bool {
		return current_edge_it == other.current_edge_it;
	}
} // namespace gdwg

#endif // GDWG_GRAPH_H
