/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.apache.tinkerpop.gremlin.tinkercat;

import io.cucumber.java.Scenario;
import org.apache.commons.configuration2.BaseConfiguration;
import org.apache.commons.configuration2.Configuration;
import org.apache.commons.configuration2.MapConfiguration;
import org.apache.tinkerpop.gremlin.LoadGraphWith;
import org.apache.tinkerpop.gremlin.TestHelper;
import org.apache.tinkerpop.gremlin.features.World;
import org.apache.tinkerpop.gremlin.process.computer.GraphComputer;
import org.apache.tinkerpop.gremlin.process.computer.traversal.strategy.decoration.VertexProgramStrategy;
import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;
import org.apache.tinkerpop.gremlin.structure.Element;
import org.apache.tinkerpop.gremlin.tinkercat.process.computer.TinkerCatComputer;
import org.apache.tinkerpop.gremlin.tinkercat.services.TinkerDegreeCentralityFactory;
import org.apache.tinkerpop.gremlin.tinkercat.services.TinkerTextSearchFactory;
import org.apache.tinkerpop.gremlin.tinkercat.structure.AbstractTinkerCat;
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerFactory;
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat;
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerTransactionGraph;
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerShuffleGraph;
import org.junit.AssumptionViolatedException;

import java.io.File;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

/**
 * The abstract {@link World} implementation for AbstractTinkerCat.
 */
public abstract class TinkerWorld implements World {
    @Override
    public String changePathToDataFile(final String pathToFileFromGremlin) {
        return ".." + File.separator + pathToFileFromGremlin;
    }

    /**
     * Get an instance of the underlying AbstractTinkerCat with the provided configuration.
     */
    public abstract AbstractTinkerCat open(final Configuration configuration);

    protected static Configuration getNumberIdManagerConfiguration() {
        final Configuration conf = new BaseConfiguration();
        conf.setProperty(TinkerCat.GREMLIN_TINKERCAT_VERTEX_ID_MANAGER, AbstractTinkerCat.DefaultIdManager.INTEGER.name());
        conf.setProperty(TinkerCat.GREMLIN_TINKERCAT_EDGE_ID_MANAGER, AbstractTinkerCat.DefaultIdManager.INTEGER.name());
        conf.setProperty(TinkerCat.GREMLIN_TINKERCAT_VERTEX_PROPERTY_ID_MANAGER, AbstractTinkerCat.DefaultIdManager.LONG.name());
        return conf;
    }

    protected static AbstractTinkerCat registerTestServices(final AbstractTinkerCat graph) {
        graph.getServiceRegistry().registerService(new TinkerTextSearchFactory(graph));
        graph.getServiceRegistry().registerService(new TinkerDegreeCentralityFactory(graph));
        return graph;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * The concrete {@link World} implementation for TinkerCat that provides the {@link GraphTraversalSource}
     * instances required by the Gherkin test suite.
     */
    public static class TinkerCatWorld extends TinkerWorld {
        private static final AbstractTinkerCat modern = registerTestServices(TinkerFactory.createModern());
        private static final AbstractTinkerCat classic = registerTestServices(TinkerFactory.createClassic());
        private static final AbstractTinkerCat crew = registerTestServices(TinkerFactory.createTheCrew());
        private static final AbstractTinkerCat sink = registerTestServices(TinkerFactory.createKitchenSink());
        private static final AbstractTinkerCat grateful = registerTestServices(TinkerFactory.createGratefulDead());

        @Override
        public GraphTraversalSource getGraphTraversalSource(final LoadGraphWith.GraphData graphData) {
            if (null == graphData)
                return registerTestServices(TinkerCat.open(getNumberIdManagerConfiguration())).traversal();
            else if (graphData == LoadGraphWith.GraphData.CLASSIC)
                return classic.traversal();
            else if (graphData == LoadGraphWith.GraphData.CREW)
                return crew.traversal();
            else if (graphData == LoadGraphWith.GraphData.MODERN)
                return modern.traversal();
            else if (graphData == LoadGraphWith.GraphData.SINK)
                return sink.traversal();
            else if (graphData == LoadGraphWith.GraphData.GRATEFUL)
                return grateful.traversal();
            else
                throw new UnsupportedOperationException("GraphData not supported: " + graphData.name());
        }

        @Override
        public AbstractTinkerCat open(final Configuration configuration) {
            return TinkerCat.open(configuration);
        }
    }

    public static class TinkerCatParameterizedWorld extends TinkerCatWorld {
        @Override
        public boolean useParametersLiterally() {
            return false;
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * The {@link World} implementation for TinkerTransactionGraph that provides the {@link GraphTraversalSource}
     * instances required by the Gherkin test suite.
     */
    public static class TinkerTransactionGraphWorld extends TinkerWorld {
        private static final AbstractTinkerCat modern;
        private static final AbstractTinkerCat classic;
        private static final AbstractTinkerCat crew;
        private static final AbstractTinkerCat sink;
        private static final AbstractTinkerCat grateful;

        static {
            modern = TinkerTransactionGraph.open(getNumberIdManagerConfiguration());
            TinkerFactory.generateModern(modern);
            modern.tx().commit();
            registerTestServices(modern);

            classic = TinkerTransactionGraph.open(getNumberIdManagerConfiguration());
            TinkerFactory.generateClassic(classic);
            classic.tx().commit();
            registerTestServices(classic);

            crew = TinkerTransactionGraph.open(getNumberIdManagerConfiguration());
            TinkerFactory.generateTheCrew(crew);
            crew.tx().commit();
            registerTestServices(crew);

            sink = TinkerTransactionGraph.open(getNumberIdManagerConfiguration());
            TinkerFactory.generateKitchenSink(sink);
            sink.tx().commit();
            registerTestServices(sink);

            grateful = TinkerTransactionGraph.open(getNumberIdManagerConfiguration());
            TinkerFactory.generateGratefulDead(grateful);
            grateful.tx().commit();
            registerTestServices(grateful);
        }

        @Override
        public GraphTraversalSource getGraphTraversalSource(final LoadGraphWith.GraphData graphData) {
            if (null == graphData)
                return registerTestServices(TinkerTransactionGraph.open(getNumberIdManagerConfiguration())).traversal();
            else if (graphData == LoadGraphWith.GraphData.CLASSIC)
                return classic.traversal();
            else if (graphData == LoadGraphWith.GraphData.CREW)
                return crew.traversal();
            else if (graphData == LoadGraphWith.GraphData.MODERN)
                return modern.traversal();
            else if (graphData == LoadGraphWith.GraphData.SINK)
                return sink.traversal();
            else if (graphData == LoadGraphWith.GraphData.GRATEFUL)
                return grateful.traversal();
            else
                throw new UnsupportedOperationException("GraphData not supported: " + graphData.name());
        }

        @Override
        public AbstractTinkerCat open(final Configuration configuration) {
            return TinkerTransactionGraph.open(configuration);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * The {@link World} implementation for TinkerShuffleGraph that provides the {@link GraphTraversalSource}
     * instances required by the Gherkin test suite.
     */
    public static class TinkerShuffleGraphWorld extends TinkerWorld {
        private static final TinkerCat modern;
        private static final TinkerCat classic;
        private static final TinkerCat crew;
        private static final TinkerCat sink;
        private static final TinkerCat grateful;

        static {
            modern = TinkerShuffleGraph.open();
            TinkerFactory.generateModern(modern);
            registerTestServices(modern);
            classic = TinkerShuffleGraph.open();
            TinkerFactory.generateClassic(classic);
            registerTestServices(classic);
            crew = TinkerShuffleGraph.open();
            TinkerFactory.generateTheCrew(crew);
            registerTestServices(crew);
            sink = TinkerShuffleGraph.open();
            TinkerFactory.generateKitchenSink(sink);
            registerTestServices(sink);
            grateful = TinkerShuffleGraph.open();
            TinkerFactory.generateGratefulDead(grateful);
            registerTestServices(grateful);
        }

        @Override
        public GraphTraversalSource getGraphTraversalSource(final LoadGraphWith.GraphData graphData) {
            if (null == graphData)
                return registerTestServices(TinkerCat.open(getNumberIdManagerConfiguration())).traversal();
            else if (graphData == LoadGraphWith.GraphData.CLASSIC)
                return classic.traversal();
            else if (graphData == LoadGraphWith.GraphData.CREW)
                return crew.traversal();
            else if (graphData == LoadGraphWith.GraphData.MODERN)
                return modern.traversal();
            else if (graphData == LoadGraphWith.GraphData.SINK)
                return sink.traversal();
            else if (graphData == LoadGraphWith.GraphData.GRATEFUL)
                return grateful.traversal();
            else
                throw new UnsupportedOperationException("GraphData not supported: " + graphData.name());
        }

        @Override
        public AbstractTinkerCat open(final Configuration configuration) {
            return TinkerShuffleGraph.open(configuration);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Enables the storing of {@code null} property values when testing. This is a terminal decorator and shouldn't be
     * used as an input into another decorator.
     */
    public static class NullWorld implements World {
        private TinkerWorld world;

        public NullWorld(TinkerWorld world) { this.world = world; }

        @Override
        public GraphTraversalSource getGraphTraversalSource(final LoadGraphWith.GraphData graphData) {
            if (graphData != null)
                throw new UnsupportedOperationException("GraphData not supported: " + graphData.name());

            final Configuration conf = getNumberIdManagerConfiguration();
            conf.setProperty(TinkerCat.GREMLIN_TINKERCAT_ALLOW_NULL_PROPERTY_VALUES, true);
            return world.open(conf).traversal();
        }

        @Override
        public void beforeEachScenario(final Scenario scenario) {
            this.world.beforeEachScenario(scenario);
        }

        @Override
        public void afterEachScenario() {
            this.world.afterEachScenario();
        }

        @Override
        public String changePathToDataFile(final String pathToFileFromGremlin) {
            return this.world.changePathToDataFile(pathToFileFromGremlin);
        }

        @Override
        public String convertIdToScript(final Object id, final Class<? extends Element> type) {
            return this.world.convertIdToScript(id, type);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Enables testing of GraphComputer functionality.
     */
    public static class ComputerWorld implements World {
        private static final Random RANDOM = TestHelper.RANDOM;

        private final World world;

        public ComputerWorld(final World world) { this.world = world; }

        @Override
        public GraphTraversalSource getGraphTraversalSource(final LoadGraphWith.GraphData graphData) {
            if (null == graphData)
                throw new AssumptionViolatedException("GraphComputer does not support mutation");

            return this.world.getGraphTraversalSource(graphData).withStrategies(VertexProgramStrategy.create(new MapConfiguration(new HashMap<String, Object>() {{
                put(VertexProgramStrategy.WORKERS, Runtime.getRuntime().availableProcessors());
                put(VertexProgramStrategy.GRAPH_COMPUTER, RANDOM.nextBoolean() ?
                        GraphComputer.class.getCanonicalName() :
                        TinkerCatComputer.class.getCanonicalName());
            }})));
        }

        @Override
        public void afterEachScenario() {
            this.world.afterEachScenario();
        }

        @Override
        public String changePathToDataFile(final String pathToFileFromGremlin) {
            return this.world.changePathToDataFile(pathToFileFromGremlin);
        }

        @Override
        public String convertIdToScript(final Object id, final Class<? extends Element> type) {
            return this.world.convertIdToScript(id, type);
        }
    }
}
