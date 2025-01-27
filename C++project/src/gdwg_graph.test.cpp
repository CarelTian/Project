#include "gdwg_graph.h"
#include <catch2/catch.hpp>

TEST_CASE("constructor") {
	auto g = gdwg::graph<std::string, int>{};
	const auto n = "hello tutor";
	CHECK(g.insert_node(n));
}

TEST_CASE("constructor-2") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	const auto n = "hello tutor";
	g.insert_node(n);
	CHECK(g.is_node("WWW"));
}

TEST_CASE("copy constructor") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	const auto n = "hello tutor";
	g.insert_node(n);
	auto new_graph = g;
	CHECK(new_graph.is_node("TTT"));
}

TEST_CASE("move constructor") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	const auto n = "hello tutor";
	g.insert_node(n);
	auto const new_graph = std::move(g);
	CHECK(new_graph.is_node("FFF"));
	CHECK(g.empty());
}

TEST_CASE("Copy Assignment") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto ng = gdwg::graph<std::string, int>{};
	ng = g;
	CHECK(ng == g);
}
TEST_CASE("print_edge") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto ue = gdwg::unweighted_edge<std::string, int>{"WWW", "FFF"};
	auto we = gdwg::weighted_edge<std::string, int>{"FFF", "TTT", 9};
	auto expected1 = "WWW -> FFF | U";
	auto expected2 = "FFF -> TTT | W | 9";
	CHECK(expected1 == ue.print_edge());
	CHECK(expected2 == we.print_edge());
}

TEST_CASE("get_weight") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto ue = gdwg::unweighted_edge<std::string, int>{"WWW", "FFF"};
	auto we = gdwg::weighted_edge<std::string, int>{"FFF", "TTT", 9};
	auto expected1 = std::nullopt;
	auto expected2 = 9;
	CHECK(expected1 == ue.get_weight());
	CHECK(expected2 == we.get_weight());
}
TEST_CASE("get_nodes") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto ue = gdwg::unweighted_edge<std::string, int>{"WWW", "FFF"};
	auto we = gdwg::weighted_edge<std::string, int>{"FFF", "TTT", 9};
	auto expected1 = std::pair<std::string, std::string>{"WWW", "FFF"};
	auto expected2 = std::pair<std::string, std::string>{"FFF", "TTT"};
	CHECK(expected1 == ue.get_nodes());
	CHECK(expected2 == we.get_nodes());
}
TEST_CASE("graph(InputIt first, InputIt last)") {
	auto list = std::vector<char>{'a', 'b', 'c', 'd'};
	auto g = gdwg::graph<char, int>(list.begin(), list.end());
	CHECK(g.is_node('a'));
	CHECK(g.is_node('b'));
	CHECK(g.is_node('c'));
	CHECK(g.is_node('d'));
	auto we = gdwg::weighted_edge<char, int>{'b', 'c', 9};
	g.insert_edge('b', 'c', 9);
	auto expected = std::pair{'b', 'c'};
	CHECK(expected == we.get_nodes());
}

TEST_CASE("operator== for edge") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto ue = gdwg::unweighted_edge<std::string, int>{"WWW", "FFF"};
	auto same = gdwg::unweighted_edge<std::string, int>{"WWW", "FFF"};
	CHECK(ue == same);
}

TEST_CASE("Insert edge") {
	auto g = gdwg::graph<std::string, int>{"WWW", "TTT", "FFF"};
	auto node = "Hello Tutor";
	g.insert_node(node);
	CHECK(g.insert_edge("WWW", "TTT", 4));
	CHECK(g.insert_edge("WWW", node));
}

TEST_CASE("Repalce Node") {
	auto g = gdwg::graph<std::string, int>{"how", "you"};
	g.insert_edge("how", "how", 3);
	g.insert_edge("you", "you", 2);
	CHECK(g.replace_node("you", "are"));
	CHECK(not g.is_node("you"));
	auto ret = g.begin();
	auto info = *ret;
	CHECK(info.from == "are");
	CHECK(info.to == "are");
}

TEST_CASE("Merge Repalce Node") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("May", "The", 3);
	g.insert_edge("The", "Your", 2);
	g.insert_edge("Warm", "The", 4);
	CHECK(g.is_connected("The", "Your"));
	CHECK(not g.is_connected("Face", "Your"));
	g.merge_replace_node("The", "Face");
	CHECK(g.is_connected("Face", "Your"));
	auto ret = g.begin();
	auto info = *ret;
	CHECK(info.from == "Face");
	CHECK(info.to == "Your");
}

TEST_CASE("Merge Repalce Node-2") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	g.insert_edge('a', 'b', 3);
	g.insert_edge('c', 'b', 2);
	g.insert_edge('d', 'b', 4);
	CHECK(g.is_connected('a', 'b'));
	CHECK(not g.is_connected('a', 'd'));
	CHECK(g.is_node('b')); // b exists in the nodes
	g.merge_replace_node('b', 'a');
	CHECK(not g.is_node('b')); // b has been removed
	CHECK(g.is_connected('d', 'a'));
	auto it1 = g.find('a', 'a', 3);
	auto it2 = g.find('c', 'a', 2);
	auto it3 = g.find('d', 'a', 4);
	CHECK(it1 != g.end());
	CHECK(it2 != g.end());
	CHECK(it3 != g.end());
}

TEST_CASE("Erase node") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("May", "Face");
	g.insert_edge("The", "Warm");
	g.insert_edge("Face", "Warm", 9);
	CHECK(g.erase_node("Face"));
	CHECK(not g.is_node("Face"));
	CHECK(g.find("May", "Face") == g.end());
	CHECK(g.find("Face", "Warm", 9) == g.end());
}

TEST_CASE("Erase edge") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("May", "Face", 9);
	g.insert_edge("Sun", "Face");
	g.insert_edge("Your", "Face");
	g.insert_edge("Sun", "Face", 6);
	CHECK(g.erase_edge("May", "Face", 9));
	CHECK(not g.is_connected("May", "Face"));
	CHECK(g.find("May", "Face", 9) == g.end());
	CHECK(g.erase_edge("Sun", "Face"));
	auto ret = g.begin();
	CHECK((*ret).weight == 6);
}

TEST_CASE("Erase edge-2") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("May", "Face", 9);
	g.insert_edge("Sun", "Face");
	g.insert_edge("Your", "Face");
	g.insert_edge("Sun", "Your", 6);
	auto b = g.begin();
	auto it = std::next(b, 2);
	g.erase_edge(it);
	it = std::next(b, 2);
	CHECK((*it).from == "Your");
	CHECK(not g.is_connected("Sun", "Your"));
	CHECK(g.find("Sun", "Your", 6) == g.end());
}

TEST_CASE("Erase edge-3") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	g.insert_edge('a', 'b', 2);
	g.insert_edge('b', 'c');
	g.insert_edge('b', 'c', 2);
	g.insert_edge('c', 'd', 7);
	g.insert_edge('d', 'c', 3);
	auto b = g.begin();
	auto i = std::next(b, 1);
	auto s = std::next(b, 4);
	g.erase_edge(i, s);
	CHECK(not g.is_connected('b', 'c'));
	CHECK(g.find('b', 'c') == g.end());
	CHECK(g.find('b', 'c', 2) == g.end());
	CHECK(g.find('c', 'd', 7) == g.end());
	CHECK(g.find('a', 'b', 2) != g.end());
	CHECK(g.find('d', 'c', 3) != g.end());
}

TEST_CASE("clear") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	g.insert_edge('a', 'b', 2);
	g.insert_edge('b', 'c');
	g.insert_edge('b', 'c', 2);
	g.insert_edge('c', 'd', 7);
	g.insert_edge('d', 'c', 3);
	g.clear();
	auto nodes = g.nodes();
	CHECK(nodes.size() == 0);
}

TEST_CASE("nodes") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	auto ret = g.nodes();
	auto expected = std::vector<std::string>{"Face", "May", "Sun", "The", "Warm", "Your"};
	CHECK(ret == expected);
}

TEST_CASE("edges") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	g.insert_edge('a', 'b', 2);
	g.insert_edge('a', 'b');
	g.insert_edge('a', 'b', 1);
	auto ret = g.edges('a', 'b');
	CHECK(not ret[0]->is_weighted());
	CHECK(ret[1]->get_weight() == 1);
	CHECK(ret[2]->get_weight() == 2);
}
TEST_CASE("connections") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("Face", "May");
	g.insert_edge("Face", "Your");
	g.insert_edge("Face", "Your", 1);
	g.insert_edge("Face", "Sun");
	g.insert_edge("Sun", "May");
	auto ret = g.connections("Face");
	auto expected = std::vector<std::string>{"May", "Sun", "Your"};
	CHECK(ret == expected);
}

TEST_CASE("begin") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("Face", "May");
	g.insert_edge("Warm", "Sun", 9);
	auto ret = g.begin();
	auto info = *ret;
	CHECK("Face" == info.from);
	CHECK("May" == info.to);
}

TEST_CASE("begin and end") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("Warm", "Sun", 9);
	g.insert_edge("Face", "May");
	g.insert_edge("Your", "Sun");
	auto ret = g.begin();
	auto edge_info = *ret;
	CHECK(edge_info.from == "Face");
	auto end = std::next(ret, 3);
	CHECK(end == g.end());
}

TEST_CASE("begin and end (null)") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	CHECK(g.begin() == g.end());
}
TEST_CASE("erase") {
	auto g = gdwg::graph<std::string, int>{"May", "The", "Sun", "Warm", "Your", "Face"};
	g.insert_edge("Face", "May", 2);
	g.insert_edge("Face", "May", 1);
	g.insert_edge("Warm", "May", 9);
	auto it = g.erase_edge("Face", "May", 2);
	CHECK(it);
	auto edge_info = *(++g.begin());
	CHECK(edge_info.from == "Warm");
	CHECK(edge_info.to == "May");
	CHECK(edge_info.weight == 9);
}

TEST_CASE("iterator ==") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd', 'e'};
	g.insert_edge('a', 'b');
	g.insert_edge('a', 'e');
	g.insert_edge('b', 'c');
	auto const a = g.begin();
	auto const b = g.begin();
	CHECK(a == b);
}

TEST_CASE("iterator *") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd', 'e'};
	g.insert_edge('a', 'b');
	g.insert_edge('a', 'e');
	g.insert_edge('b', 'c');
	auto const a = g.begin();
	CHECK((*a).to == 'b');
}

TEST_CASE("edge operator") {
	auto a = std::make_shared<gdwg::unweighted_edge<char, int>>('a', 'c');
	auto b = std::make_shared<gdwg::weighted_edge<char, int>>('a', 'b', 3);
	CHECK(*a > *b);
}

TEST_CASE("find") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd', 'e'};
	g.insert_edge('a', 'b');
	g.insert_edge('a', 'e');
	g.insert_edge('b', 'c');
	CHECK(g.is_connected('b', 'c'));
	auto it = g.find('b', 'c');
	auto ret = *it;
	CHECK(ret.from == 'b');
	g.erase_edge(it);
	CHECK(not g.is_connected('b', 'c'));
}
TEST_CASE("<<") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'e'};
	g.insert_edge('a', 'b');
	g.insert_edge('a', 'e');
	g.insert_edge('a', 'c', 2);
	g.insert_edge('b', 'c');
	auto out = std::ostringstream{};
	out << g;
	auto const expected = std::string_view(R"(
a (
  a -> b | U
  a -> c | W | 2
  a -> e | U
)
b (
  b -> c | U
)
c (
)
e (
)
)");
	CHECK(out.str() == expected);
}

TEST_CASE("insert_edge-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.insert_edge('6', '7', 6),
	                    "Cannot call gdwg::graph<N, E>::insert_edge when either src or dst node does not exist");
	REQUIRE_THROWS_AS(g.insert_edge('6', '7', 6), std::runtime_error);
}

TEST_CASE("replace node-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.replace_node('6', 'd'),
	                    "Cannot call gdwg::graph<N, E>::replace_node on a node that doesn't exist");
	REQUIRE_THROWS_AS(g.replace_node('6', 'd'), std::runtime_error);
}

TEST_CASE("merge replace node-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.merge_replace_node('a', 'z'),
	                    "Cannot call gdwg::graph<N, E>::merge_replace_node on old or new data if they don't exist in "
	                    "the graph");
	REQUIRE_THROWS_AS(g.merge_replace_node('a', 'z'), std::runtime_error);
}

TEST_CASE("erase edge-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.erase_edge('a', 'z'),
	                    "Cannot call gdwg::graph<N, E>::erase_edge on src or dst if they don't exist in the graph");
	REQUIRE_THROWS_AS(g.erase_edge('a', 'z'), std::runtime_error);
}

TEST_CASE("is connected edge-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.is_connected('a', 'z'),
	                    "Cannot call gdwg::graph<N, E>::is_connected if src or dst node don't exist in the graph");
	REQUIRE_THROWS_AS(g.is_connected('a', 'z'), std::runtime_error);
}

TEST_CASE("edges-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.edges('a', 'z'),
	                    "Cannot call gdwg::graph<N, E>::edges if src or dst node don't exist in the graph");
	REQUIRE_THROWS_AS(g.edges('a', 'z'), std::runtime_error);
}
TEST_CASE("connections-exception") {
	auto g = gdwg::graph<char, int>{'a', 'b', 'c', 'd'};
	REQUIRE_THROWS_WITH(g.connections('z'),
	                    "Cannot call gdwg::graph<N, E>::connections if src doesn't exist in the graph");
	REQUIRE_THROWS_AS(g.connections('z'), std::runtime_error);
}